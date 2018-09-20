import rules

from .models import RoleAssignment, SODAR_CONSTANTS

# SODAR constants
PROJECT_ROLE_OWNER = SODAR_CONSTANTS['PROJECT_ROLE_OWNER']
PROJECT_ROLE_DELEGATE = SODAR_CONSTANTS['PROJECT_ROLE_DELEGATE']
PROJECT_ROLE_CONTRIBUTOR = SODAR_CONSTANTS['PROJECT_ROLE_CONTRIBUTOR']
PROJECT_ROLE_GUEST = SODAR_CONSTANTS['PROJECT_ROLE_GUEST']
PROJECT_TYPE_CATEGORY = SODAR_CONSTANTS['PROJECT_TYPE_CATEGORY']


# Predicates -------------------------------------------------------------


@rules.predicate
def is_project_owner(user, obj):
    """Whether or not the user has the role of project owner"""
    assignment = RoleAssignment.objects.get_assignment(user, obj)

    if assignment:
        return assignment.role.name == PROJECT_ROLE_OWNER

    return False


@rules.predicate
def is_project_delegate(user, obj):
    """Whether or not the user has the role of project delegate"""
    assignment = RoleAssignment.objects.get_assignment(user, obj)

    if assignment:
        return assignment.role.name == PROJECT_ROLE_DELEGATE

    return False


@rules.predicate
def is_project_contributor(user, obj):
    """Whether or not the user has the role of project contributor"""
    assignment = RoleAssignment.objects.get_assignment(user, obj)

    if assignment:
        return assignment.role.name == PROJECT_ROLE_CONTRIBUTOR

    return False


@rules.predicate
def is_project_guest(user, obj):
    """Whether or not the user has the role of project guest"""
    assignment = RoleAssignment.objects.get_assignment(user, obj)

    if assignment:
        return assignment.role.name == PROJECT_ROLE_GUEST

    return False


@rules.predicate
def has_project_role(user, obj):
    """Whether or not the user has any role in the project"""
    return RoleAssignment.objects.get_assignment(user, obj) is not None


@rules.predicate
def has_category_child_role(user, obj):
    """Whether or not the user has any role in any child project under the
    current one, if the current project is a category"""
    return obj.type == PROJECT_TYPE_CATEGORY and obj.has_role(
        user, include_children=True)


@rules.predicate
def has_roles(user):
    """Whether or not the user has any roles set in the system"""
    return RoleAssignment.objects.filter(user=user).count() > 0


# Rules ------------------------------------------------------------------


# Rules should not be needed, use permissions for user rights


# Permissions ------------------------------------------------------------


# Allow viewing project/category details
rules.add_perm(
    'projectroles.view_project',
    rules.is_superuser | has_project_role | has_category_child_role)

# Allow project updating
rules.add_perm(
    'projectroles.update_project',
    rules.is_superuser | is_project_owner | is_project_delegate)

# Allow creation of projects
rules.add_perm(
    'projectroles.create_project',
    rules.is_superuser | is_project_owner)

# Allow updating project settings
rules.add_perm(
    'projectroles.update_project_settings',
    rules.is_superuser | is_project_owner | is_project_delegate)

# Allow viewing project roles
rules.add_perm(
    'projectroles.view_project_roles',
    rules.is_superuser | is_project_owner | is_project_delegate |
    is_project_contributor | is_project_guest)

# Allow updating project owner
rules.add_perm(
    'projectroles.update_project_owner',
    rules.is_superuser | is_project_owner)

# Allow updating project delegate
rules.add_perm(
    'projectroles.update_project_delegate',
    rules.is_superuser | is_project_owner)

# Allow updating project members
rules.add_perm(
    'projectroles.update_project_members',
    rules.is_superuser | is_project_owner | is_project_delegate)

# Allow inviting users to project via email
rules.add_perm(
    'projectroles.invite_users',
    rules.is_superuser | is_project_owner | is_project_delegate)

# Allow importing roles from another project
rules.add_perm(
    'projectroles.import_roles',
    rules.is_superuser | is_project_owner)
