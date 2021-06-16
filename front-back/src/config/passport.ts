import { NativeError } from "mongoose";
import { Request, Response, NextFunction } from "express";
import passport from "passport";
import { Profile, Strategy as TwitterStrategy } from "passport-twitter";
import { Strategy as LocalStrategy } from "passport-local";
import { User, UserDocument } from "../models/User";
import config from "./config";


passport.use(
  new LocalStrategy({ usernameField: "email" }, async (email, password, done) => {
      await User.findOne({email: email}, async (err: NativeError, user: UserDocument) => {
        if (err) { return done(err); }
        if (!user) {
            return done(undefined, false, {message: "El email introducido no está registrado"});
        }
        const match = await user.matchPassword(password);
        if (!match) {
            return done(undefined, false, {message: "La contraseña es incorrecta"});
        } else{
            return done (undefined, user);
        }
      });
  })
);

passport.use(
    new TwitterStrategy({
        consumerKey: config.TWITTER.CONSUMER_KEY,
        consumerSecret: config.TWITTER.CONSUMER_SECRET,
        callbackURL: config.TWITTER.CALLBACK_URL,
        passReqToCallback: true,
        userAuthorizationURL: 'https://api.twitter.com/oauth/authorize'
    },
    async function(req: Request, token: String, tokenSecret: String, profile: Profile, cb){
        var result = await User.findByIdAndUpdate(req.user, {twitter_ids : profile.id}, {new : true})
        if (result != null){
            result.twitter_ids = profile.id;
        }
        return cb(null, result);
    }
));


passport.serializeUser<any, any>((req, user, done) => {
    done(undefined, user);
});


passport.deserializeUser<UserDocument>((id, done) => {
    User.findById(id, (err: NativeError, user: UserDocument) => done(err, user));
});

export const isAuthenticated = (req: Request, res: Response, next: NextFunction) => {
    if (req.isAuthenticated()) {
        return next();
    }
    req.flash("error_msg", "Debes iniciar sesión antes");
    res.redirect("/users/signin");
};
