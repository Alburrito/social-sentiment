import app from "./app";
import https from "https";
import fs from "fs";

https.createServer({
    cert: fs.readFileSync('./src/cert.pem'),
    key: fs.readFileSync('./src/key.pem')
}, app).listen(app.get("port"));

console.log(`Server on port ${app.get('port')}`);
