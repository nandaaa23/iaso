// @ts-ignore
import { useSafeIntl } from 'bluesquare-components';
import { IntlFormatMessage } from '../../../types/intl';

import { DropdownOptions } from '../../../types/utils';

import MESSAGES from '../messages';

export const useGetStatus = (): Array<DropdownOptions<string>> => {
    const { formatMessage }: { formatMessage: IntlFormatMessage } =
        useSafeIntl();
    return [
        {
            value: 'DRAFT',
            label: formatMessage(MESSAGES.draft),
        },
        {
            value: 'UNPUBLISHED',
            label: formatMessage(MESSAGES.unpublished),
        },
        {
            value: 'PUBLISHED',
            label: formatMessage(MESSAGES.published),
        },
    ];
};
