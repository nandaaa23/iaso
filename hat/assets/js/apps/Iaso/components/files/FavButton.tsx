import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import { IconButton, Tooltip } from '@mui/material';
import { useSafeIntl } from 'bluesquare-components';
import React, { FunctionComponent } from 'react';
import { defineMessages } from 'react-intl';
import { ShortFile } from '../../domains/instances/types/instance';

const styles = {
    favButton: {
        position: 'absolute',
        top: 8,
        right: 8,
        backgroundColor: 'rgba(255, 255, 255, 0.7)',
        boxShadow: '0 0 10px rgba(0, 0, 0, 0.2)',
        '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
        },
    },
};
const MESSAGES = defineMessages({
    setAsDefault: {
        id: 'iaso.orgUnit.setAsDefaultImage',
        defaultMessage: 'Set as default image',
    },
    removeAsDefault: {
        id: 'iaso.orgUnit.removeAsDefaultImage',
        defaultMessage: 'Remove as default image',
    },
});

type Props = {
    file: ShortFile;
    // eslint-disable-next-line no-unused-vars
    onImageFavoriteClick: (id: number) => void;
    // eslint-disable-next-line no-unused-vars
    isDefaultImage: (id: number) => boolean;
};

export const FavButton: FunctionComponent<Props> = ({
    file,
    onImageFavoriteClick,
    isDefaultImage,
}) => {
    const isDefault = isDefaultImage(file.itemId);
    const { formatMessage } = useSafeIntl();
    const title = isDefault
        ? formatMessage(MESSAGES.removeAsDefault)
        : formatMessage(MESSAGES.setAsDefault);
    return (
        <Tooltip title={title}>
            <IconButton
                color="primary"
                sx={styles.favButton}
                onClick={() => onImageFavoriteClick(file.itemId)}
            >
                {!isDefault && <FavoriteBorderIcon />}
                {isDefault && <FavoriteIcon />}
            </IconButton>
        </Tooltip>
    );
};
