"""SODAR Taskflow API for Django apps"""

import logging
import requests
from uuid import UUID

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Projectroles dependency
from projectroles.models import SODAR_CONSTANTS


logger = logging.getLogger(__name__)

# SODAR constants
PROJECT_TYPE_PROJECT = SODAR_CONSTANTS['PROJECT_TYPE_PROJECT']

# Local constants
HEADERS = {'Content-Type': 'application/json'}
TARGETS = (
    settings.TASKFLOW_TARGETS
    if hasattr(settings, 'TASKFLOW_TARGETS')
    else ['sodar']
)
TASKFLOW_TEST_MODE = (
    True
    if (hasattr(settings, 'TASKFLOW_TEST_MODE') and settings.TASKFLOW_TEST_MODE)
    else False
)


class TaskflowAPI:
    """SODAR Taskflow API to be used by Django apps"""

    class FlowSubmitException(Exception):
        """SODAR Taskflow submission exception"""

        pass

    class CleanupException(Exception):
        """SODAR Taskflow cleanup exception"""

        pass

    def __init__(self):
        self.taskflow_url = '{}:{}'.format(
            settings.TASKFLOW_BACKEND_HOST, settings.TASKFLOW_BACKEND_PORT
        )

    def submit(
        self,
        project_uuid,
        flow_name,
        flow_data,
        request=None,
        targets=TARGETS,
        request_mode='sync',
        timeline_uuid=None,
        force_fail=False,
        sodar_url=None,
    ):
        """
        Submit taskflow for SODAR project data modification.

        :param project_uuid: UUID of the project (UUID object or string)
        :param flow_name: Name of flow to be executed (string)
        :param flow_data: Input data for flow execution (dict)
        :param request: Request object (optional)
        :param targets: Names of backends to sync with (list)
        :param request_mode: "sync" or "async"
        :param timeline_uuid: UUID of corresponding timeline event (optional)
        :param force_fail: Make flow fail on purpose (boolean, default False)
        :param sodar_url: URL of SODAR server (optional, for testing)
        :return: Boolean
        :raise: FlowSubmitException if submission fails
        """
        url = self.taskflow_url + '/submit'

        # Format UUIDs in flow_data
        for k, v in flow_data.items():
            if type(v) == UUID:
                flow_data[k] = str(v)

        data = {
            'project_uuid': str(project_uuid),
            'flow_name': flow_name,
            'flow_data': flow_data,
            'request_mode': request_mode,
            'targets': targets,
            'force_fail': force_fail,
            'timeline_uuid': str(timeline_uuid),
            'sodar_secret': settings.TASKFLOW_SODAR_SECRET,
        }

        # Add the "test_mode" parameter
        data['test_mode'] = TASKFLOW_TEST_MODE

        # HACK: Add overriding URL for test server
        if request:
            if request.POST and 'sodar_url' in request.POST:
                data['sodar_url'] = request.POST['sodar_url']

            elif request.GET and 'sodar_url' in request.GET:
                data['sodar_url'] = request.GET['sodar_url']

        elif sodar_url:
            data['sodar_url'] = sodar_url

        logger.debug('Submit data: {}'.format(data))
        response = requests.post(url, json=data, headers=HEADERS)

        if response.status_code == 200 and bool(response.text) is True:
            logger.debug('Submit OK')
            return True

        else:
            logger.error('Submit failed: {}'.format(response.text))
            raise self.FlowSubmitException(
                self.get_error_msg(flow_name, response.text)
            )

    def use_taskflow(self, project):
        """
        Check whether taskflow use is allowed with a project.

        :param project: Project object
        :return: Boolean
        """
        return True if project.type == PROJECT_TYPE_PROJECT else False

    def cleanup(self):
        """
        Send a cleanup command to SODAR Taskflow. Only allowed in test mode.

        :return: Boolean
        :raise: ImproperlyConfigured if TASKFLOW_TEST_MODE is not set True
        :raise: CleanupException if SODAR Taskflow raises an error
        """
        if not TASKFLOW_TEST_MODE:
            raise ImproperlyConfigured(
                'TASKFLOW_TEST_MODE not True, cleanup command not allowed'
            )

        url = self.taskflow_url + '/cleanup'
        data = {'test_mode': TASKFLOW_TEST_MODE}

        response = requests.post(url, json=data, headers=HEADERS)

        if response.status_code == 200:
            logger.debug('Cleanup OK')
            return True

        else:
            logger.debug('Cleanup failed: {}'.format(response.text))
            raise self.CleanupException(response.text)

    def get_error_msg(self, flow_name, submit_info):
        """
        Return a printable version of a SODAR Taskflow error message.

        :param flow_name: Name of submitted flow
        :param submit_info: Returned information from SODAR Taskflow
        :return: String
        """
        return 'Taskflow "{}" failed! Reason: "{}"'.format(
            flow_name, submit_info[:256]
        )
