"""Views for the timeline Django app"""

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from rest_framework.response import Response

# Projectroles dependency
from projectroles.models import Project, SODAR_CONSTANTS
from projectroles.utils import get_display_name
from projectroles.views import (
    LoggedInPermissionMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
    BaseTaskflowAPIView,
)

from .models import ProjectEvent


# Local variables
DEFAULT_PAGINATION = 15


class ProjectTimelineView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
    ListView,
):
    """View for displaying files and folders for a project"""

    permission_required = 'timeline.view_timeline'
    template_name = 'timeline/timeline.html'
    model = ProjectEvent
    paginate_by = (
        settings.TIMELINE_PAGINATION
        if hasattr(settings, 'TIMELINE_PAGINATION')
        else DEFAULT_PAGINATION
    )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['timeline_title'] = '{} Timeline'.format(
            get_display_name(
                SODAR_CONSTANTS['PROJECT_TYPE_PROJECT'], title=True
            )
        )
        context['timeline_mode'] = 'project'
        return context

    def get_queryset(self):
        set_kwargs = {'project__sodar_uuid': self.kwargs['project']}

        if not self.request.user.has_perm(
            'timeline.view_classified_event', self.get_permission_object()
        ):
            set_kwargs['classified'] = False

        return ProjectEvent.objects.filter(**set_kwargs).order_by('-pk')


class ObjectTimelineView(ProjectTimelineView):
    """View for displaying files and folders for a project"""

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['timeline_title'] = '{} Timeline'.format(
            self.kwargs['object_model']
        )
        context['timeline_mode'] = 'object'

        return context

    def get_queryset(self):
        project = Project.objects.get(sodar_uuid=self.kwargs['project'])

        queryset = ProjectEvent.objects.get_object_events(
            project=project,
            object_model=self.kwargs['object_model'],
            object_uuid=self.kwargs['object_uuid'],
        )

        if not self.request.user.has_perm(
            'timeline.view_classified_event', self.get_permission_object()
        ):
            queryset = queryset.filter(classified=False)

        return queryset


# Taskflow API Views -----------------------------------------------------------


class TaskflowEventStatusSetAPIView(BaseTaskflowAPIView):
    def post(self, request):
        try:
            tl_event = ProjectEvent.objects.get(
                sodar_uuid=request.data['event_uuid']
            )

        except ProjectEvent.DoesNotExist:
            return Response('Timeline event not found', status=404)

        try:
            tl_event.set_status(
                status_type=request.data['status_type'],
                status_desc=request.data['status_desc'],
                extra_data=request.data['extra_data']
                if 'extra_data' in request.data
                else None,
            )

        except TypeError:
            return Response('Invalid status type', status=400)

        return Response('ok', status=200)
