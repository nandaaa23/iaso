import React, { FunctionComponent, ReactNode } from 'react';
import { Tab, Tooltip } from '@mui/material';
import { makeStyles } from '@mui/styles';
import InfoIcon from '@mui/icons-material/Info';
import classnames from 'classnames';

export const useStyles = makeStyles(theme => ({
    tab: {
        '&.MuiTab-root': {
            display: 'inline-flex',
            flexDirection: 'row-reverse',
        },
    },
    tabError: {
        color: `${theme.palette.error.main} !important`,
    },
    tabDisabled: {
        cursor: 'default',
    },
    tabIcon: {
        position: 'relative',
        top: 1,
        left: theme.spacing(0.5),
        cursor: 'pointer',
    },
}));

type Tab = {
    title: string;
    form: ReactNode;
    hasTabError: boolean;
    key: string;
    disabled?: boolean;
};

type Props = {
    value: number | string;
    title: string;
    hasTabError: boolean;
    disabled: boolean;
    showIcon: boolean;
    tooltipMessage: string;
};

export const TabWithInfoIcon: FunctionComponent<Props> = ({
    title,
    hasTabError,
    disabled,
    tooltipMessage,
    showIcon = false,
    // passed from Mui Tabs component
    ...props
}) => {
    const classes: Record<string, string> = useStyles();
    return (
        // @ts-ignore
        <Tab
            label={title}
            className={classnames(
                classes.tab,
                hasTabError && classes.tabError,
                disabled && classes.tabDisabled,
            )}
            disableFocusRipple={disabled}
            disableRipple={disabled}
            disabled={disabled}
            icon={
                (showIcon && (
                    <Tooltip title={tooltipMessage}>
                        <InfoIcon
                            fontSize="small"
                            className={classes.tabIcon}
                        />
                    </Tooltip>
                )) || <></>
            }
            // eslint-disable-next-line react/jsx-props-no-spreading
            {...props}
        />
    );
};
