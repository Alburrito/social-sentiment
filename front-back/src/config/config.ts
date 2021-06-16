export default {
    PORT: process.env.PORT || 'error',
    DB: {
        HOST: process.env.DB_HOST || 'localhost',
        PORT: process.env.DB_PORT || 'error',
        DBNAME: process.env.DB_NAME || 'socialsentiment',
        URI: `mongodb://${process.env.MONGO_HOST || 'localhost'}:${process.env.MONGO_PORT || 'error'}/${process.env.MONGO_DBNAME || 'socialsentiment'}`,
        USER: process.env.MONGO_USER,
        PASSWORD: process.env.MONGO_PASSWORD
    },
    API: {
        HOST: 'http://'+process.env.API_HOST || 'http://localhost',
        PORT: process.env.API_PORT || 'error',
        URI: `http://${process.env.API_HOST || 'localhost'}:${process.env.API_PORT || 'error'}`
    },
    TWITTER: {
        CONSUMER_KEY: process.env.TWITTER_API_KEY || 'error',
        CONSUMER_SECRET: process.env.TWITTER_SECRET_API_KEY || 'error',
        CALLBACK_URL: process.env.CALLBACK_URL || 'error/callback'
    }
};