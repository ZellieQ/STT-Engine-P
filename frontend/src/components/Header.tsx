import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { logout } from '../store/slices/authSlice';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Box,
  useMediaQuery,
  useTheme,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import DashboardIcon from '@mui/icons-material/Dashboard';
import HistoryIcon from '@mui/icons-material/History';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import MicIcon from '@mui/icons-material/Mic';
import Link from 'next/link';

const Header = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    dispatch(logout());
    handleClose();
    router.push('/');
  };

  const toggleDrawer = (open: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
    if (
      event.type === 'keydown' &&
      ((event as React.KeyboardEvent).key === 'Tab' || (event as React.KeyboardEvent).key === 'Shift')
    ) {
      return;
    }
    setDrawerOpen(open);
  };

  const drawerContent = () => (
    <Box
      sx={{ width: 250 }}
      role="presentation"
      onClick={toggleDrawer(false)}
      onKeyDown={toggleDrawer(false)}
    >
      <List>
        <ListItem sx={{ py: 2 }}>
          <Typography variant="h6">STT Engine</Typography>
        </ListItem>
        <Divider />
        <ListItem button onClick={() => router.push('/dashboard')}>
          <ListItemIcon>
            <DashboardIcon />
          </ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItem>
        <ListItem button onClick={() => router.push('/dashboard')}>
          <ListItemIcon>
            <HistoryIcon />
          </ListItemIcon>
          <ListItemText primary="My Transcriptions" />
        </ListItem>
        <ListItem button onClick={() => router.push('/profile')}>
          <ListItemIcon>
            <AccountCircleIcon />
          </ListItemIcon>
          <ListItemText primary="Profile" />
        </ListItem>
        <ListItem button onClick={() => router.push('/settings')}>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
      </List>
      <Divider />
      <List>
        <ListItem button onClick={handleLogout}>
          <ListItemIcon>
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText primary="Logout" />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <AppBar position="static">
      <Toolbar>
        {isAuthenticated && isMobile && (
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
            onClick={toggleDrawer(true)}
          >
            <MenuIcon />
          </IconButton>
        )}
        
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          <Link href={isAuthenticated ? '/dashboard' : '/'} passHref style={{ textDecoration: 'none', color: 'inherit', display: 'flex', alignItems: 'center' }}>
            <MicIcon sx={{ mr: 1 }} />
            STT Engine
          </Link>
        </Typography>
        
        {isAuthenticated ? (
          <>
            {!isMobile && (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Button color="inherit" onClick={() => router.push('/dashboard')}>
                  Dashboard
                </Button>
                <Button color="inherit" onClick={() => router.push('/dashboard')}>
                  My Transcriptions
                </Button>
              </Box>
            )}
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <AccountCircleIcon />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={() => { handleClose(); router.push('/profile'); }}>Profile</MenuItem>
              <MenuItem onClick={() => { handleClose(); router.push('/settings'); }}>Settings</MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </>
        ) : (
          <>
            <Button color="inherit" onClick={() => router.push('/login')}>Login</Button>
            <Button color="inherit" onClick={() => router.push('/register')}>Register</Button>
          </>
        )}
      </Toolbar>
      
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
      >
        {drawerContent()}
      </Drawer>
    </AppBar>
  );
};

export default Header;
