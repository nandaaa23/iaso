import MenuIcon from '@mui/icons-material/Menu';
import { Box, Container, Grid, IconButton } from '@mui/material';
import { makeStyles } from '@mui/styles';
import React, { FunctionComponent, useContext } from 'react';
import { Link } from 'react-router-dom';
import { CurrentUserInfos } from '../../components/nav/CurrentUser';
import { LogoutButton } from '../../components/nav/LogoutButton';
import iasoBg from '../../images/iaso-bg.jpg';
import { useCurrentUser } from '../../utils/usersUtils';
import { LogoSvg } from '../app/components/LogoSvg';
import SidebarMenuComponent from '../app/components/SidebarMenuComponent';
import { useSidebar } from '../app/contexts/SideBarContext';
import { ThemeConfigContext } from '../app/contexts/ThemeConfigContext';
import { LangSwitch } from './components/LangSwitch';
import { useHomeButtons } from './hooks/useHomeButtons';

const useStyles = makeStyles(theme => ({
    root: {
        width: '100vw',
        height: '100vh',
        overflow: 'auto',
        backgroundRepeat: 'repeat-y',
        backgroundPosition: 'center',
        backgroundSize: '100%',
        display: 'flex',
        alignItems: 'center',
    },
    logo: {
        textAlign: 'center',
        '& svg': { filter: 'drop-shadow(0px 0px 24px rgba(0, 0, 0, 0.24))' },
        '& img': { filter: 'drop-shadow(0px 0px 24px rgba(0, 0, 0, 0.24))' },
    },
    text: {
        fontFamily: '"DINAlternate-Bold", "DIN Alternate", sans-serif',
        fontSize: 25,
        textAlign: 'center',
        textTransform: 'uppercase',
        // @ts-ignore
        color: theme.palette.gray.main,
        width: '50vw',
    },
    login: {
        textAlign: 'center',
        marginTop: theme.spacing(2),
    },
    topMenu: {
        position: 'absolute',
        top: 0,
        left: 0,
        '& span[class*="currentUserInfos"]:first-child': {
            fontSize: 19,
        },

        '& span[class*="account"]': {
            fontSize: 14,
        },
    },
    container: {
        width: '70%',
        marginTop: theme.spacing(2),
    },
    logoButton: {
        color: theme.palette.primary.main,
        textDecoration: 'none !important',
        width: '100%',
        padding: theme.spacing(2),
        border: `2px solid ${theme.palette.primary.main}`,
        borderRadius: theme.spacing(2),
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
        alignItems: 'center',
        transition: 'transform .2s ease, background-color .2s ease',
        filter: 'drop-shadow(2px 5px 5px rgba(0, 0, 0, 0.24));',
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        '&:hover': {
            transform: 'scale(1.07, 1.07)',
            backgroundColor: 'rgba(255, 255, 255, 1)',
        },
        '& svg': {
            fontSize: 60,
        },
        '& span': {
            fontSize: 15,
            textTransform: 'uppercase',
            display: 'flex',
            marginTop: theme.spacing(1),
            width: '100%',
            textAlign: 'center',
            alignItems: 'center',
            justifyContent: 'center',
            height: 30,
        },
    },
}));
export const HomeOnline: FunctionComponent = () => {
    const classes = useStyles();
    const { LOGO_PATH, APP_TITLE } = useContext(ThemeConfigContext);
    const { toggleSidebar } = useSidebar();
    const homeButtons = useHomeButtons();
    const currentUser = useCurrentUser();
    return (
        <Box
            className={classes.root}
            sx={{ backgroundImage: `url("${window.STATIC_URL}${iasoBg}")` }}
        >
            <Grid className={classes.topMenu} container spacing={2}>
                <Grid container item xs={6} justifyContent="flex-start">
                    <Box m={2}>
                        <IconButton
                            color="inherit"
                            aria-label="Menu"
                            onClick={toggleSidebar}
                            id="menu-button"
                        >
                            <MenuIcon />
                        </IconButton>
                        <SidebarMenuComponent location={window.location} />
                    </Box>
                </Grid>
                <Grid container item xs={6} justifyContent="flex-end">
                    <Box
                        display="flex"
                        alignItems="center"
                        justifyContent="flex-end"
                    >
                        <CurrentUserInfos
                            currentUser={currentUser}
                            version={(window as any).IASO_VERSION}
                        />
                    </Box>
                    <Box
                        pr={4}
                        pt={4}
                        pb={4}
                        display="flex"
                        alignItems="center"
                    >
                        <Box pl={2} display="inline-flex">
                            <LangSwitch />
                        </Box>
                        <Box pl={2}>
                            <LogoutButton color="primary" />
                        </Box>
                    </Box>
                </Grid>
            </Grid>
            <Container maxWidth="md">
                <Box
                    justifyContent="center"
                    alignItems="center"
                    display="flex"
                    flexDirection="column"
                >
                    <Box>
                        <Box className={classes.logo}>
                            {APP_TITLE !== 'Iaso' && LOGO_PATH && (
                                <img
                                    alt="logo"
                                    src={`${window.STATIC_URL}${LOGO_PATH}`}
                                    style={{ width: 150, height: 'auto' }}
                                />
                            )}
                            {APP_TITLE === 'Iaso' && (
                                <LogoSvg width={150} height={160} />
                            )}
                        </Box>
                    </Box>
                </Box>

                <Container className={classes.container} maxWidth="sm">
                    <Grid container spacing={2} justifyContent="center">
                        {homeButtons.map(button => (
                            <Grid item xs={12} sm={6} md={4} key={button.label}>
                                <Link
                                    className={classes.logoButton}
                                    key={button.label}
                                    to={button.url}
                                    // setting state to null in anticipation to breadcrumbs implementation
                                    // It has no impact at the moment
                                    state={null}
                                >
                                    {button.Icon}
                                    <span>{button.label}</span>
                                </Link>
                            </Grid>
                        ))}
                    </Grid>
                </Container>
            </Container>
        </Box>
    );
};
