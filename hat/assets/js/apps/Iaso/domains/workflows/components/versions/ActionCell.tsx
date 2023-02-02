import React, { FunctionComponent } from 'react';

import { IconButton as IconButtonComponent } from 'bluesquare-components';
import { Box, makeStyles } from '@material-ui/core';
import FileCopyIcon from '@material-ui/icons/FileCopy';
import BlockIcon from '@material-ui/icons/Block';

import { WorkflowVersion } from '../../types';

import MESSAGES from '../../messages';
import { baseUrls } from '../../../../constants/urls';
import DeleteDialog from '../../../../components/dialogs/DeleteDialogComponent';
import { PublishVersionIconModal } from './PublishVersionModal';

import { useCopyWorkflowVersion } from '../../hooks/requests/useCopyWorkflowVersion';
import { useDeleteWorkflowVersion } from '../../hooks/requests/useDeleteWorkflowVersion';
import { useUpdateWorkflowVersion } from '../../hooks/requests/useUpdateWorkflowVersion';

type Props = {
    workflowVersion: WorkflowVersion;
    entityTypeId: number;
};

const useStyles = makeStyles(theme => ({
    publishIcon: {
        display: 'inline-block',
        '& svg': {
            color: theme.palette.success.main,
        },
    },
}));

export const VersionsActionCell: FunctionComponent<Props> = ({
    workflowVersion,
    entityTypeId,
}) => {
    const classes = useStyles();
    const { version_id: versionId, status } = workflowVersion;
    const { mutate: copyWorkflowVersion } = useCopyWorkflowVersion();
    const { mutate: deleteWorkflowVersion } = useDeleteWorkflowVersion();
    const { mutate: updateWorkflowVersion } = useUpdateWorkflowVersion(
        'workflowVersions',
        versionId,
        false,
    );
    const icon = status === 'DRAFT' ? 'edit' : 'remove-red-eye';
    const tooltipMessage = status === 'DRAFT' ? MESSAGES.edit : MESSAGES.see;
    return (
        <>
            <IconButtonComponent
                url={`${baseUrls.workflowDetail}/entityTypeId/${entityTypeId}/versionId/${versionId}`}
                icon={icon}
                tooltipMessage={tooltipMessage}
            />
            {status !== 'DRAFT' && (
                <IconButtonComponent
                    onClick={() => copyWorkflowVersion(versionId)}
                    overrideIcon={FileCopyIcon}
                    tooltipMessage={MESSAGES.copy}
                />
            )}
            {status === 'DRAFT' && (
                <DeleteDialog
                    keyName={`workflow-version-${versionId}`}
                    titleMessage={MESSAGES.deleteTitle}
                    message={MESSAGES.deleteText}
                    onConfirm={() => deleteWorkflowVersion(versionId)}
                />
            )}
            {status !== 'PUBLISHED' && (
                <Box className={classes.publishIcon}>
                    <PublishVersionIconModal
                        workflowVersion={workflowVersion}
                        invalidateQueryKey="workflowVersions"
                    />
                </Box>
            )}
            {status === 'PUBLISHED' && (
                <IconButtonComponent
                    onClick={() =>
                        updateWorkflowVersion({ status: 'UNPUBLISHED' })
                    }
                    overrideIcon={BlockIcon}
                    tooltipMessage={MESSAGES.unpublish}
                    color="error"
                />
            )}
        </>
    );
};
