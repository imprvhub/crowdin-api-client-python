from datetime import timezone, datetime
from unittest import mock

import pytest

from crowdin_api.api_resources.enums import PatchOperation
from crowdin_api.api_resources.users.enums import (
    ListProjectMembersCrowdinOrderBy,
    ListProjectMembersEnterpriseOrderBy,
    UserRole,
    UserPatchPath,
    ListGroupManagersOrderBy,
    ListUsersOrderBy,
    UserStatus,
    UserTwoFactorAuthStatus,
    OrganizationRole,
    ProjectRole
)
from crowdin_api.api_resources.users.resource import (
    UsersResource,
    BaseUsersResource,
    EnterpriseUsersResource,
)
from crowdin_api.requester import APIRequester
from crowdin_api.sorting import Sorting, SortingOrder, SortingRule


class TestBaseUsersResource:
    resource_class = BaseUsersResource

    def get_resource(self, base_absolut_url):
        return self.resource_class(requester=APIRequester(base_url=base_absolut_url))

    def test_resource_with_id(self, base_absolut_url):
        project_id = 1
        resource = self.resource_class(
            requester=APIRequester(base_url=base_absolut_url), project_id=project_id
        )
        assert resource.get_project_id() == project_id

    @pytest.mark.parametrize(
        "incoming_data, path",
        (
            ({"projectId": 1}, "projects/1/members"),
            ({"projectId": 1, "memberId": 2}, "projects/1/members/2"),
        ),
    )
    def test_get_members_path(self, incoming_data, path, base_absolut_url):

        resource = self.get_resource(base_absolut_url)
        assert resource.get_members_path(**incoming_data) == path

    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_get_authenticated_user(self, m_request, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.get_authenticated_user() == "response"
        m_request.assert_called_once_with(method="get", path="user")


class TestUsersResource:
    resource_class = UsersResource

    def get_resource(self, base_absolut_url):
        return self.resource_class(requester=APIRequester(base_url=base_absolut_url))

    @pytest.mark.parametrize(
        "name_method",
        [
            "get_authenticated_user",
            "get_members_path",
            "list_project_members",
            "get_member_info",
        ]
    )
    def test_present_methods(self, name_method):
        assert hasattr(self.resource_class, name_method)

    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_get_member_info(self, m_request, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.get_member_info(projectId=1, memberId=2) == "response"
        m_request.assert_called_once_with(method="get", path="projects/1/members/2")

    @pytest.mark.parametrize(
        "in_params, request_params",
        (
            (
                {},
                {
                    "orderBy": None,
                    "search": None,
                    "role": None,
                    "languageId": None,
                    "offset": 0,
                    "limit": 25,
                },
            ),
            (
                {
                    "orderBy": Sorting(
                        [
                            SortingRule(
                                ListProjectMembersCrowdinOrderBy.ID, SortingOrder.DESC
                            )
                        ]
                    ),
                    "search": "search",
                    "role": UserRole.BLOCKED,
                    "languageId": "ua",
                    "offset": 0,
                    "limit": 25,
                },
                {
                    "orderBy": Sorting(
                        [
                            SortingRule(
                                ListProjectMembersCrowdinOrderBy.ID, SortingOrder.DESC
                            )
                        ]
                    ),
                    "search": "search",
                    "role": UserRole.BLOCKED,
                    "languageId": "ua",
                    "offset": 0,
                    "limit": 25,
                },
            ),
        ),
    )
    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_list_project_members(self, m_request, in_params, request_params, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.list_project_members(projectId=1, **in_params) == "response"
        m_request.assert_called_once_with(
            method="get", params=request_params, path="projects/1/members"
        )


class TestEnterpriseUsersResource:
    resource_class = EnterpriseUsersResource

    def get_resource(self, base_absolut_url):
        return self.resource_class(requester=APIRequester(base_url=base_absolut_url))

    @pytest.mark.parametrize(
        "name_method",
        [
            "get_authenticated_user",
            "get_members_path",
            "get_users_path",
            "list_project_members",
            "add_project_member",
            "replace_project_member_permissions",
            "delete_member_from_project",
            "invite_user",
            "edit_user",
            "delete_user",
            "add_project_member",
            "replace_project_member_permissions",
            "delete_member_from_project",
        ]
    )
    def test_present_methods(self, name_method):
        assert hasattr(self.resource_class, name_method)

    @pytest.mark.parametrize(
        "userId, path",
        (
            (None, "users"),
            (1, "users/1"),
        ),
    )
    def test_get_users_path(self, userId, path, base_absolut_url):

        resource = self.get_resource(base_absolut_url)
        assert resource.get_users_path(userId=userId) == path

    @pytest.mark.parametrize(
        "group_id, user_id, path",
        (
            (1, None, "groups/1/managers"),
            (1, 2000, "groups/1/managers/2000")
        )
    )
    def test_get_group_managers_path(self, group_id, user_id, path, base_absolut_url):
        resource = self.get_resource(base_absolut_url)
        assert resource.get_group_managers_path(group_id, user_id) == path

    @pytest.mark.parametrize(
        "in_params, request_params",
        (
            (
                {},
                {
                    "team_ids": None,
                    "order_by": None
                },
            ),
            (
                {
                    "team_ids": [1, 2, 3],
                    "order_by": Sorting(
                        [
                            SortingRule(
                                ListGroupManagersOrderBy.ID,
                                SortingOrder.DESC,
                            )
                        ]
                    ),
                },
                {
                    "team_ids": "1,2,3",
                    "order_by": Sorting(
                        [
                            SortingRule(
                                ListGroupManagersOrderBy.ID,
                                SortingOrder.DESC,
                            )
                        ]
                    ),
                }
            )
        )
    )
    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_list_group_managers(self, m_request, in_params, request_params, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.list_group_managers(group_id=1, **in_params) == "response"
        m_request.assert_called_once_with(
            method="get",
            path="groups/1/managers",
            params=request_params
        )

    @pytest.mark.parametrize(
        "in_params, request_params",
        (
            (
                [
                    {
                        "op": "add",
                        "path": "/-",
                        "value": {
                            "userId": 18
                        }
                    },
                    {
                        "op": "remove",
                        "path": "/24"
                    }
                ],
                [
                    {
                        "op": "add",
                        "path": "/-",
                        "value": {
                            "userId": 18
                        }
                    },
                    {
                        "op": "remove",
                        "path": "/24"
                    }
                ],
            ),
        )
    )
    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_update_group_managers(self, m_request, in_params, request_params, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.update_group_managers(group_id=1, request_data=in_params) == "response"
        m_request.assert_called_once_with(
            method="patch",
            path="groups/1/managers",
            request_data=request_params
        )

    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_get_group_manager(self, m_request, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.get_group_manager(group_id=1, user_id=2) == "response"
        m_request.assert_called_once_with(
            method="get",
            path="groups/1/managers/2"
        )

    @pytest.mark.parametrize(
        "in_params, request_params",
        (
            (
                {},
                {
                    "orderBy": None,
                    "search": None,
                    "workflowStepId": None,
                    "languageId": None,
                    "offset": 0,
                    "limit": 25,
                },
            ),
            (
                {
                    "orderBy": Sorting(
                        [
                            SortingRule(
                                ListProjectMembersEnterpriseOrderBy.ID,
                                SortingOrder.DESC,
                            )
                        ]
                    ),
                    "search": "search",
                    "workflowStepId": 72,
                    "languageId": "ua",
                    "offset": 0,
                    "limit": 25,
                },
                {
                    "orderBy": Sorting(
                        [
                            SortingRule(
                                ListProjectMembersEnterpriseOrderBy.ID,
                                SortingOrder.DESC,
                            )
                        ]
                    ),
                    "search": "search",
                    "workflowStepId": 72,
                    "languageId": "ua",
                    "offset": 0,
                    "limit": 25,
                },
            ),
        ),
    )
    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_list_project_members(self, m_request, in_params, request_params, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.list_project_members(projectId=1, **in_params) == "response"
        m_request.assert_called_once_with(
            method="get", params=request_params, path="projects/1/members"
        )

    @pytest.mark.parametrize(
        "in_params, request_params",
        (
            (
                {"email": ""},
                {
                    "email": "",
                    "firstName": None,
                    "lastName": None,
                    "timezone": None
                },
            ),
            (
                {
                    "email": "john@example.com",
                    "firstName": "Jon",
                    "lastName": "Doe",
                    "timezone": "America/New_York"
                },
                {
                    "email": "john@example.com",
                    "firstName": "Jon",
                    "lastName": "Doe",
                    "timezone": "America/New_York"
                },
            ),
        ),
    )
    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_invite_user(self, m_request, in_params, request_params, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.invite_user(**in_params) == "response"
        m_request.assert_called_once_with(
            method="post", path="users", request_data=request_params
        )

    @pytest.mark.parametrize(
        "in_params, request_params",
        (
            (
                {
                    "userIds": [1]
                },
                {
                    "userIds": [1],
                    "accessToAllWorkflowSteps": None,
                    "managerAccess": None,
                    "permissions": None,
                    "roles": None
                },
            ),
            (
                {
                    "userIds": [1],
                    "accessToAllWorkflowSteps": False,
                    "managerAccess": False,
                    "permissions": {
                        "it": {"workflowStepIds": [313]},
                        "de": {"workflowStepIds": "all"}
                    },
                    "roles": [
                        {
                            "name": "translator",
                            "permissions": {
                                "allLanguages": False,
                                "languagesAccess": {
                                    "uk": {
                                        "allContent": False,
                                        "workflowStepIds": [882]
                                    },
                                    "it": {
                                        "allContent": True
                                    }
                                }
                            }
                        },
                        {
                            "name": "proofreader",
                            "permissions": {
                                "allLanguages": True,
                                "languagesAccess": []
                            }
                        }
                    ]
                },
                {
                    "userIds": [
                        1
                    ],
                    "accessToAllWorkflowSteps": False,
                    "managerAccess": False,
                    "permissions": {
                        "it": {"workflowStepIds": [313]},
                        "de": {"workflowStepIds": "all"}
                    },
                    "roles": [
                        {
                            "name": "translator",
                            "permissions": {
                                "allLanguages": False,
                                "languagesAccess": {
                                    "uk": {
                                        "allContent": False,
                                        "workflowStepIds": [882]
                                    },
                                    "it": {
                                        "allContent": True
                                    }
                                }
                            }
                        },
                        {
                            "name": "proofreader",
                            "permissions": {
                                "allLanguages": True,
                                "languagesAccess": []
                            }
                        }
                    ]
                },
            ),
        ),
    )
    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_add_project_member(self, m_request, in_params, request_params, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.add_project_member(projectId=1, **in_params) == "response"
        m_request.assert_called_once_with(
            method="post", path="projects/1/members", request_data=request_params
        )

    @pytest.mark.parametrize(
        "in_params, request_params",
        (
            (
                {},
                {
                    "accessToAllWorkflowSteps": None,
                    "managerAccess": None,
                    "permissions": None,
                    "roles": None
                },
            ),
            (
                {
                    "accessToAllWorkflowSteps": False,
                    "managerAccess": False,
                    "permissions": {
                        "it": {"workflowStepIds": [313]},
                        "de": {"workflowStepIds": "all"}
                    },
                    "roles": [
                        {
                            "name": "translator",
                            "permissions": {
                                "allLanguages": False,
                                "languagesAccess": {
                                    "uk": {
                                        "allContent": False,
                                        "workflowStepIds": [882]
                                    },
                                    "it": {
                                        "allContent": True
                                    }
                                }
                            }
                        },
                        {
                            "name": "proofreader",
                            "permissions": {
                                "allLanguages": True,
                                "languagesAccess": []
                            }
                        }
                    ]
                },
                {
                    "accessToAllWorkflowSteps": False,
                    "managerAccess": False,
                    "permissions": {
                        "it": {"workflowStepIds": [313]},
                        "de": {"workflowStepIds": "all"}
                    },
                    "roles": [
                        {
                            "name": "translator",
                            "permissions": {
                                "allLanguages": False,
                                "languagesAccess": {
                                    "uk": {
                                        "allContent": False,
                                        "workflowStepIds": [882]
                                    },
                                    "it": {
                                        "allContent": True
                                    }
                                }
                            }
                        },
                        {
                            "name": "proofreader",
                            "permissions": {
                                "allLanguages": True,
                                "languagesAccess": []
                            }
                        }
                    ]
                },
            ),
        ),
    )
    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_replace_project_member_permissions(
            self, m_request, in_params, request_params, base_absolut_url
    ):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.replace_project_member_permissions(
            projectId=1, memberId=1, **in_params
        ) == "response"

        m_request.assert_called_once_with(
            method="put", path="projects/1/members/1", request_data=request_params
        )

    @pytest.mark.parametrize(
        "in_params, request_params",
        (
            (
                [{
                    "value": 4,
                    "op": PatchOperation.REPLACE,
                    "path": UserPatchPath.FIRST_NAME
                }],
                [{
                    "value": 4,
                    "op": PatchOperation.REPLACE,
                    "path": UserPatchPath.FIRST_NAME
                }],
            ),
        ),
    )
    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_edit_user(self, m_request, in_params, request_params, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.edit_user(userId=1, data=in_params) == "response"
        m_request.assert_called_once_with(
            method="patch", path="users/1", request_data=request_params
        )

    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_delete_user(self, m_request, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.delete_user(userId=1) == "response"
        m_request.assert_called_once_with(method="delete", path="users/1")

    @pytest.mark.parametrize(
        "in_params, request_params",
        (
            (
                {
                    "limit": 10,
                    "offset": 2,
                    "order_by": Sorting(
                        [
                            SortingRule(ListUsersOrderBy.CREATED_AT, SortingOrder.DESC),
                            SortingRule(ListUsersOrderBy.USERNAME)
                        ]
                    ),
                    "status": UserStatus.ACTIVE,
                    "search": "Alex",
                    "two_factor": UserTwoFactorAuthStatus.ENABLED,
                    "organization_roles": [
                        OrganizationRole.MANAGER,
                        OrganizationRole.VENDOR,
                        OrganizationRole.CLIENT
                    ],
                    "team_id": 123,
                    "project_ids": [11, 22, 33],
                    "project_roles": [
                        ProjectRole.MANAGER,
                        ProjectRole.DEVELOPER,
                        ProjectRole.LANGUAGE_COORDINATOR
                    ],
                    "language_ids": ["uk", "es", "it"],
                    "group_ids": [4, 5, 6],
                    "last_seen_from": datetime(2024, 1, 10, 10, 41, 33, tzinfo=timezone.utc),
                    "last_seen_to": datetime(2024, 1, 11, 10, 41, 33, tzinfo=timezone.utc)
                },
                {
                    "limit": 10,
                    "offset": 2,
                    "orderBy": Sorting(
                        [
                            SortingRule(ListUsersOrderBy.CREATED_AT, SortingOrder.DESC),
                            SortingRule(ListUsersOrderBy.USERNAME)
                        ]
                    ),
                    "status": "active",
                    "search": "Alex",
                    "twoFactor": "enabled",
                    "organizationRoles": "manager,vendor,client",
                    "teamId": 123,
                    "projectIds": "11,22,33",
                    "projectRoles": "manager,developer,language_coordinator",
                    "languageIds": "uk,es,it",
                    "groupIds": "4,5,6",
                    "lastSeenFrom": "2024-01-10T10:41:33+00:00",
                    "lastSeenTo": "2024-01-11T10:41:33+00:00"
                }
            ),
        )
    )
    @mock.patch("crowdin_api.requester.APIRequester.request")
    def test_list_users(self, m_request, in_params, request_params, base_absolut_url):
        m_request.return_value = "response"

        resource = self.get_resource(base_absolut_url)
        assert resource.list_users(**in_params)
        m_request.assert_called_once_with(
            method="get",
            path="users",
            params=request_params
        )
