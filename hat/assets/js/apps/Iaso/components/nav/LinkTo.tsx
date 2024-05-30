import { makeStyles } from '@mui/styles';
import {
    IconButtonBuiltInIcon,
    IconButton,
    IntlMessage,
    LinkWithLocation,
    textPlaceholder,
    useKeyPressListener,
} from 'bluesquare-components';
import classNames from 'classnames';
import React, { FunctionComponent } from 'react';

import MESSAGES from './messages';

export type IconVariant = IconButtonBuiltInIcon;

type Props = {
    condition: boolean;
    url: string;
    text?: string;
    useIcon?: boolean;
    className?: string;
    replace?: boolean;
    iconSize?: 'small' | 'medium' | 'large' | 'default' | 'inherit';
    size?: 'small' | 'medium' | 'large' | 'default' | 'inherit';
    tooltipMessage?: IntlMessage;
    color?: string;
    target?: '_blank' | '_self' | '_parent' | '_top';
    icon?: IconVariant;
};

const useStyles = makeStyles(() => ({
    link: {
        cursor: 'pointer',
    },
}));

export const LinkTo: FunctionComponent<Props> = ({
    condition,
    url,
    text,
    useIcon = false,
    className = '',
    replace = false,
    iconSize = 'medium',
    size = 'medium',
    target = '_self',
    color,
    tooltipMessage = MESSAGES.see,
    icon = 'remove-red-eye',
}) => {
    const targetBlankEnabled = useKeyPressListener('Meta');
    const actualTarget = targetBlankEnabled ? '_blank' : target;
    const classes: Record<string, string> = useStyles();
    if (condition) {
        if (useIcon) {
            return (
                <IconButton
                    icon={icon}
                    tooltipMessage={tooltipMessage}
                    iconSize={iconSize}
                    size={size}
                    reloadDocument={targetBlankEnabled}
                    url={url}
                    replace={replace}
                    color={color}
                    target={actualTarget}
                />
            );
        }
        return (
            <LinkWithLocation
                className={classNames(className, classes.link)}
                reloadDocument={targetBlankEnabled}
                to={url}
                replace={replace}
                target={actualTarget}
            >
                {text || textPlaceholder}
            </LinkWithLocation>
        );
    }
    if (useIcon) return null;
    return <>{text || textPlaceholder}</>;
};
