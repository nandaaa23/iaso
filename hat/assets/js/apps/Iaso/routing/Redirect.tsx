import React, { FunctionComponent } from 'react';
import { Navigate, useParams } from 'react-router-dom';

type Props = {
    to: string; // redirection url
    path: any;
};

/**
 * Wrapper for react-router-dom `<Navigate/>`. Manually replaces param values in destination url
 *
 */
export const Redirect: FunctionComponent<Props> = ({ to, path }) => {
    const params = useParams();
    let destination = to;
    const keysToConvert = Object.keys(path?.conversions ?? {});
    Object.entries(params).forEach(([key, value]) => {
        if (keysToConvert.includes(key)) {
            destination = destination.replace(
                `:${path.conversions[key]}`,
                `${value}`,
            );
        } else {
            destination = destination.replace(`:${key}`, `${value}`);
        }
    });
    if (params['*']) {
        destination = `${destination}${params['*']}`;
    }

    return <Navigate to={`${destination}`} relative="path" />;
};
