import { Router } from 'express';
import passport from 'passport';

const router: Router = Router(); 

router.get('/auth/twitter', passport.authorize('twitter', {failureRedirect : '/network/twitter/bindAccount',
                                                            successRedirect : '/network/twitter/dashboard'}));

router.get('/auth/twitter/callback', 
  passport.authorize('twitter', {successRedirect: '/network/twitter/dashboard', 
                                    failureRedirect: '/users/signin' }),
  function(req, res) {
    res.redirect('/network/twitter/dashboard');
  });

export default router;