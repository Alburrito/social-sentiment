import { Schema, model, Document } from "mongoose";
import bcrypt from "bcryptjs";

export type UserDocument = Document & {
  username: string;
  email: string;
  password: string;
  twitter_ids: string;
  instagram_ids: string;
  facebook_ids: string;
  youtube_ids: string;
  encryptPassword(password: string): Promise<string>;
  matchPassword(password: string): Promise<Boolean>;
}

const UserSchema = new Schema<UserDocument>(
  {
    username: { type: String, required: true, unique: true },
    email: { type: String, required: true, unique: true },
    password: {
      type: String,
      required: true,
    },
    twitter_ids: { type: String, required: true},
    instagram_ids: { type: String, required: true},
    facebook_ids: { type: String, required: true},
    youtube_ids: { type: String, required: true},
  },
  {
    timestamps: true,
  }
);

UserSchema.methods.encryptPassword = async (password) => {
  const salt = await bcrypt.genSalt();
  return await bcrypt.hash(password, salt);
};

UserSchema.methods.matchPassword = async function (
  this: UserDocument,
  password: string
): Promise<Boolean> {
  return await bcrypt.compare(password, this.password);
};

export const User = model<UserDocument>("User", UserSchema);