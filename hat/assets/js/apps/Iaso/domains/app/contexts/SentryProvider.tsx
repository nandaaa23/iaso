import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import * as Sentry from '@sentry/browser';
import React, {
    createContext,
    FunctionComponent,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useState,
} from 'react';

type SentryContextType = {
    hasConsent: boolean;
    setConsent: (consent: boolean) => void;
};

export type SentryConfig = {
    SENTRY_DSN?: string;
    SENTRY_ENVIRONMENT?: string;
};

type Props = {
    children: React.ReactNode;
};

const SentryContext = createContext<SentryContextType | undefined>(undefined);

export const useSentry = () => {
    const context = useContext(SentryContext);
    if (!context) {
        throw new Error('useSentry must be used within SentryProvider');
    }
    return context;
};
const initSentry = (consent: boolean) => {
    // Return early if no consent or no DSN
    if (!consent || !window.sentry_config?.SENTRY_DSN) return;

    Sentry.init({
        dsn: window.sentry_config.SENTRY_DSN,
        environment: window.sentry_config.SENTRY_ENVIRONMENT || 'development',
        replaysSessionSampleRate: 0.1,
        replaysOnErrorSampleRate: 1.0,
        integrations: [
            Sentry.replayIntegration({
                maskAllText: false,
                blockAllMedia: false,
                networkDetailAllowUrls: [
                    window.location.origin,
                    `${window.location.origin}/api`,
                ],
            }),
        ],
    });
};

export const SentryProvider: FunctionComponent<Props> = ({ children }) => {
    const [showDialog, setShowDialog] = useState(false);
    const [hasConsent, setHasConsent] = useState(
        () => localStorage.getItem('sentry-consent') === 'true',
    );

    useEffect(() => {
        const hasStoredConsent = localStorage.getItem('sentry-consent');
        if (hasStoredConsent === null && window.sentry_config?.SENTRY_DSN) {
            setShowDialog(true);
        }
    }, []);

    const handleConsent = useCallback((consent: boolean) => {
        localStorage.setItem('sentry-consent', consent.toString());
        setHasConsent(consent);
        initSentry(consent);
        setShowDialog(false);
    }, []);

    const contextValue = useMemo(
        () => ({ hasConsent, setConsent: handleConsent }),
        [handleConsent, hasConsent],
    );
    return (
        <SentryContext.Provider value={contextValue}>
            {children}
            <Dialog open={showDialog} onClose={() => handleConsent(false)}>
                <DialogTitle>Analytics Consent</DialogTitle>
                <DialogContent>
                    We use Sentry to collect session replay data to improve our
                    service quality and debug issues. This includes recording
                    your interactions with our application. Your privacy is
                    important to us, and you can change this setting at any
                    time.
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => handleConsent(false)}>
                        Decline
                    </Button>
                    <Button
                        onClick={() => handleConsent(true)}
                        variant="contained"
                    >
                        Accept
                    </Button>
                </DialogActions>
            </Dialog>
        </SentryContext.Provider>
    );
};

// const YourSettingsComponent = () => {
//     const { hasConsent, setConsent } = useSentry();

//     return (
//         <FormControlLabel
//             control={
//                 <Switch
//                     checked={hasConsent}
//                     onChange={(e) => setConsent(e.target.checked)}
//                 />
//             }
//             label="Allow session recording for improved support"
//         />
//     );
// };
