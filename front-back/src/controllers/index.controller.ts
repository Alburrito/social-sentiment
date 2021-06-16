import { Request, Response } from "express";

class IndexController {

    public index (req: Request, res: Response) {
        res.render("index", { title: 'Social Sentiment', errors: []});
    }

    public about (req: Request, res: Response) {
        res.render("about", { title: 'Acerca de la plataforma', errors: []});
    }

}

export const indexController = new IndexController();