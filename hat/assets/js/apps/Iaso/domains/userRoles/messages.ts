import { defineMessages } from 'react-intl';

const MESSAGES = defineMessages({
    title: {
        defaultMessage: 'User roles',
        id: 'iaso.userRoles.title',
    },
    search: {
        defaultMessage: 'Search',
        id: 'iaso.search',
    },
    name: {
        defaultMessage: 'Name',
        id: 'iaso.label.name',
    },
    created_at: {
        defaultMessage: 'Created',
        id: 'iaso.label.created_at',
    },
    updated_at: {
        defaultMessage: 'Updated',
        id: 'iaso.label.updated_at',
    },
    actions: {
        defaultMessage: 'Action(s)',
        id: 'iaso.label.actions',
    },
    delete: {
        id: 'iaso.userRoles.delete',
        defaultMessage: 'Are you sure you want to delete this user role?',
    },
    deleteError: {
        id: 'iaso.snackBar.deleteUserRoleError',
        defaultMessage: 'An error occurred while deleting user role',
    },
    deleteSuccess: {
        id: 'iaso.snackBar.delete_successful',
        defaultMessage: 'Deleted successfully',
    },
});

export default MESSAGES;
