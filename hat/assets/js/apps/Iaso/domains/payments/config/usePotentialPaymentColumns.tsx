import { useMemo } from 'react';
import { useSafeIntl, Column, IntlFormatMessage } from 'bluesquare-components';
import MESSAGES from '../messages';
import { PotentialPayment } from '../types';
import { textPlaceholder } from '../../../constants/uiConstants';

export const usePotentialPaymentColumns = (): Column[] => {
    const { formatMessage }: { formatMessage: IntlFormatMessage } =
        useSafeIntl();
    return useMemo(() => {
        const columns: Column[] = [
            {
                Header: formatMessage(MESSAGES.lastName),
                id: 'user__last_name',
                accessor: 'user.last_name',
                Cell: ({
                    value,
                }: {
                    value: PotentialPayment['user']['last_name'];
                }): string => {
                    return value || textPlaceholder;
                },
            },
            {
                Header: formatMessage(MESSAGES.firstName),
                id: 'user__first_name',
                accessor: 'user.first_name',
                Cell: ({
                    value,
                }: {
                    value: PotentialPayment['user']['first_name'];
                }): string => {
                    return value || textPlaceholder;
                },
            },
            {
                Header: formatMessage(MESSAGES.userName),
                id: 'user__username',
                accessor: 'user.username',
                Cell: ({
                    value,
                }: {
                    value: PotentialPayment['user']['username'];
                }): string => {
                    return value || textPlaceholder;
                },
            },
            //  TODO: we should add user phone number here
        ];
        return columns;
    }, [formatMessage]);
};
