import { Router } from 'express';
import { isAuthenticated } from "../config/passport";
const router: Router = Router(); 

import { networkController, hasSocialNetworkBinded }  from '../controllers/network.controller';

router.get('/network/twitter/dashboard', isAuthenticated, hasSocialNetworkBinded, networkController.twitterDashboardView);
router.get('/network/twitter/records', isAuthenticated, hasSocialNetworkBinded, networkController.twitterRecordsView);
router.get('/network/twitter/bindAccount', isAuthenticated, networkController.twitterBindAccountView);

router.get('/network/instagram/dashboard', isAuthenticated, hasSocialNetworkBinded, networkController.instagramDashboardView);
router.get('/network/instagram/bindAccount', isAuthenticated, networkController.instagramBindAccountView);

router.get('/network/facebook/dashboard', isAuthenticated, hasSocialNetworkBinded, networkController.facebookDashboardView);
router.get('/network/facebook/bindAccount', isAuthenticated, networkController.facebookBindAccountView);

router.get('/network/youtube/dashboard', isAuthenticated, hasSocialNetworkBinded, networkController.youtubeDashboardView);
router.get('/network/youtube/bindAccount', isAuthenticated, networkController.youtubeBindAccountView);


export default router;