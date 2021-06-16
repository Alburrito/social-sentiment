import { NextFunction, Request, Response } from "express";
import { User, UserDocument } from "../models/User";
import passport from "passport";
import { IVerifyOptions } from "passport-local";
import "../config/passport";

class UsersController {
  public signUpView(req: Request, res: Response) {
    res.render("users/signup", { title: "Registro", username: "", email: "" , errors: []});
  }

  public async signUp(req: Request, res: Response) {
    const errors = [];
    const { username, email, password, repeatPassword } = req.body;

    if (!username) {
      errors.push({ text: "Se debe introducir un nombre de usuario." });
    }

    if (!email) {
      errors.push({ text: "Se debe introducir un correo electrónico" });
    }

    if (!password) {
      errors.push({ text: "Se debe introducir una contraseña" });
    } else {
      if (password.length < 8) {
        errors.push({
          text: "La contraseña debe tener al menos 8 caracteres.",
        });
      }
      if (!repeatPassword) {
        errors.push({ text: "Se debe confirmar la contraseña por seguridad." });
      } else if (password != repeatPassword) {
        errors.push({ text: "Las contraseñas deben coincidir." });
      }
    }

    if (errors.length > 0) {
      res.render("users/signup", {
        errors,
        username,
        email,
        title: "Registro",
      });
    } else {
      const sameEmail = await User.findOne({ email: email });
      const sameUsername = await User.findOne({ username: username });
      if (sameEmail) {
        errors.push({ text: "El email introducido ya está registrado" });
      }
      if (sameUsername) {
        errors.push({
          text: "El nombre de usuario introducido ya está registrado",
        });
      }
      if (errors.length > 0) {
        res.render("users/signup", {
          errors,
          title: "Registro",
        });
      } else {
        const newUser = new User({ 
          username, email, password,
          twitter_ids : "-1",
          instagram_ids : "-1",
          facebook_ids : "-1",
          youtube_ids : "-1", });
        newUser.password = await newUser.encryptPassword(password);
        await newUser.save();
        req.flash("success_msg", "Cuenta registrada con éxito. Por favor, inicia sesión.");
        res.redirect("/users/signin");
      }
    }
  }

  public signInView(req: Request, res: Response) {
    res.render("users/signin", { title: "Inicio de sesión", errors: [] });
  }

  public signIn(req: Request, res: Response, next: NextFunction) {
    passport.authenticate("local", (err: Error, user: UserDocument, info: IVerifyOptions) => {
        if (err) { return next(err); }
        if (!user) {
            req.flash("error_msg", "Fallo al iniciar sesión");
            return res.redirect("/users/signin");
        }
        req.logIn(user, (err) => {
            if (err) { return next(err); }
            req.flash("success_msg", "Inicio de sesión correcto");
            res.redirect("/");
        });
    })(req, res, next);
  }

  public logout(req: Request, res: Response) {
      req.logout();
      req.flash("success_msg", "Sesión cerrada satisfactoriamente");
      res.redirect("/");
  }
}

export const usersController = new UsersController();
