import { Request, Response, NextFunction } from "express";
import request from "request-promise-native";

import config from '../config/config';
import { User } from "../models/User";

class NetworkController {

    // TWITTER

    public async twitterDashboardView(req: Request, res: Response) {
        var baseUrl = config.API.URI 
        var endpoint = '/twitter/dashboard_stats';
        var user = await User.findById(res.locals.user);
        if(user != null){
            var queryString = '?twitter_id='+user.twitter_ids;
            var uri = baseUrl + endpoint + queryString
            request.get(uri, {json:true }, (err, response) => {
                if (err) {
                    return console.log(err);
                }
                if (response.statusCode == 400 ||
                    response.statusCode == 404 ||
                    response.statusCode == 500){
                    res.render("network/twitter/nodata", {title:'¡Lo sentimos!', errors:[]});
                }
                else{
                    const result = response.body;
                    const profile_info = result.profile_info;
                    const stats = result.stats;
                    const top_tweets = result.top_tweets;
                    const sentiment = JSON.stringify(result.sentiment);
        
                    res.render("network/twitter/dashboard", {layout: "../views/layouts/dashboardLayout", title: "Panel de Twitter", errors: [],
                                                            profile_info: profile_info, stats: stats, top_tweets: top_tweets, sentiment: sentiment});
                }
            });
        } 
    }

    public async twitterRecordsView(req: Request, res: Response) {
        var baseUrl = config.API.URI 
        var endpoint = '/twitter/record_stats';
        var user = await User.findById(res.locals.user);
        if(user != null){
            var queryString = '?twitter_id='+user.twitter_ids;
            var uri = baseUrl + endpoint + queryString
            request.get(uri, {json:true }, (err, response) => {
                if (err) {
                    return console.log(err);
                }
                if (response.statusCode == 400 ||
                    response.statusCode == 404 ||
                    response.statusCode == 500){
                    res.render("network/twitter/nodata", {title:'¡Lo sentimos!', errors:[]});
                }
                else{
                    const result = JSON.stringify(response.body);
                    res.render("network/twitter/records", {layout: "../views/layouts/dashboardLayout", title: "Historial de Twitter", errors: [], result: result})
                }
            });
        }
    }

    public twitterBindAccountView(req: Request, res: Response) {
        res.render("network/twitter/bindAccount", {layout: "../views/layouts/dashboardLayout", title: "Asociar cuenta de Twitter", errors: []})
    }



    // INSTAGRAM

    public instagramDashboardView(req: Request, res: Response) {
        res.render("network/instagram/dashboard", {layout: "../views/layouts/dashboardLayout", title: "Instagram Dashboard", errors: []});
    }

    public instagramBindAccountView(req: Request, res: Response) {
        res.render("network/instagram/bindAccount", {layout: "../views/layouts/dashboardLayout", title: "Asociar cuenta de Instagram", errors: []})
    }

    public instagramBindAccount(req: Request, res: Response) {
        res.send('CUENTA BINDEADA');
    }


    // FACEBOOK

    public facebookDashboardView(req: Request, res: Response) {
        res.render("network/facebook/dashboard", {layout: "../views/layouts/dashboardLayout", title: " Facebook Dashboard", errors: []});
    }

    public facebookBindAccountView(req: Request, res: Response) {
        res.render("network/facebook/bindAccount", {layout: "../views/layouts/dashboardLayout", title: "Asociar cuenta de Facebook", errors: []})
    }

    public facebookBindAccount(req: Request, res: Response) {
        res.send('CUENTA BINDEADA');
    }


    // YOUTUBE

    public youtubeDashboardView(req: Request, res: Response) {
        res.render("network/youtube/dashboard", {layout: "../views/layouts/dashboardLayout", title: "Youtube Dashboard", errors: []});
    }

    public youtubeBindAccountView(req: Request, res: Response) {
        res.render("network/twitter/bindAccount", {layout: "../views/layouts/dashboardLayout", title: "Asociar cuenta de Youtube", errors: []})
    }

    public youtubeBindAccount(req: Request, res: Response) {
        res.send('CUENTA BINDEADA');
    }
}

export const networkController = new NetworkController();

export const hasSocialNetworkBinded = async ( req: Request, res: Response, next: NextFunction) => {
    const dbUser = await User.findOne({ email: res.locals.user.email });
    const url = req.url;
    const network = url.split('/')[2]
    
    switch(network) {
        case 'twitter':
            if (dbUser?.twitter_ids == "-1"){
                req.flash("error_msg", "Debes vincular tu cuenta de Twitter antes");
                res.redirect("/network/twitter/bindAccount");
                return;
            }
            break;
        
        case 'instagram':
            if (dbUser?.instagram_ids == "-1"){
                req.flash("error_msg", "Debes vincular tu cuenta de Instagram antes");
                res.redirect("/network/instagram/bindAccount");
                return;
            }
            break;

        case 'facebook':
            if (dbUser?.facebook_ids == "-1"){
                req.flash("error_msg", "Debes vincular tu cuenta de Facebook antes");
                res.redirect("/network/facebook/bindAccount");
                return;
            }
            break;

        case 'youtube':
            if (dbUser?.youtube_ids == "-1"){
                req.flash("error_msg", "Debes vincular tu cuenta de Youtube antes");
                res.redirect("/network/youtube/bindAccount");
                return;
            }
            break;
    }

    return next();
};
