import express from "express";
import { Request, Response, NextFunction } from "express";
import path from "path";
import morgan from "morgan";
require("ejs");
import favicon from "serve-favicon";
import expressLayouts from "express-ejs-layouts";
import session from "express-session";
import flash from "connect-flash";
import passport from "passport";


import config from "./config/config";
import indexRoutes from "./routes/index.routes";
import usersRoutes from "./routes/users.routes";
import networkRoutes from "./routes/network.routes";
import twitterAuthenticationRoutes from "./routes/authenticate-twitter.routes"

// Inicializaciones
const app = express();
require("./database");

// Configuracion
app.set("port", config.PORT);
app.set("views", path.join(__dirname, "views"));
app.set("layouts", path.join(app.get("views"), "layouts"));
app.set("layout", path.join(app.get("layouts"), "layout"));
app.set("view engine", "ejs");

// Middlewares
app.use(morgan("dev"));
app.use(favicon(path.join(__dirname, "static", "img", "favicon.ico")));
app.use(express.urlencoded({ extended: false }));
app.use(express.json());
app.use(expressLayouts);
app.use(
  session({
    secret: "",
    resave: true,
    saveUninitialized: true,
    cookie: { secure: true },
  })
);
app.use(passport.initialize());
app.use(passport.session());
app.use(flash());

// Variables globales
app.use((req: Request, res: Response, next: NextFunction) => {
  res.locals.error_msg = req.flash("error_msg");
  res.locals.success_msg = req.flash("success_msg");
  res.locals.user = req.user || undefined;
  next();
});

// Rutas
app.use(indexRoutes);
app.use(usersRoutes);
app.use(networkRoutes);
app.use(twitterAuthenticationRoutes);

// Ficheros estaticos
app.use(express.static(path.join(__dirname, "static")));

export default app;
