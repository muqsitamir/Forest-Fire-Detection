# GUIDE: BINDING REACT FRONTEND WITH DJANGO 

### Prerequisites:
To follow this guide you should have the following:
1) Have python and node installed on your system.
2) Activate a virtual environment for python to work with.
3) Have atleast one app in a django project.

> Note: If you have any of the above requirement unsatisfied you can refer to the appropriate guide below.

Step 0: Changing directory to django projects root and activating the virtual environment.
```shell script
cd wwf_snow_leopard
activate venv/bin/activate
```

Step 1: Install `django-webpack-loader` and add it to the `requirements.txt`
```shell script
pip django-webpack-loader==1.0.0
echo django-webpack-loader==1.0.0 >> requirements.txt
```

Step 2: 
```shell script
mkdir frontend
cd frontend
mkdir assets
```

Step 2: Add following lines in project/settings.py
```
INSTALLED_APPS = [
  ...
  'rest_framework',
  'webpack_loader',
  ...
]
```

Also, add the path to the templates directory to the DIRS key on the TEMPLATES 
variable and the one to assets to STATICFILES_DIRS so that Django finds the static files there.

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)

Also configure webpack loader in settings.py
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'dist/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}



Step 4:
npm init

After running this command package.json will appear and a directory for node modules will be created.
Now create the assets/src/js/index.js file. It will be the entry point of the application.
mkdir -p assets/src/js
touch assets/src/js/index.js

Now we will configure webpack, but before this we wil add webpack tracker to register the status of webpack
npm install --save-dev webpack webpack-bundle-tracker

Step 5:


Configure React
npm install --save react react-dom

Add Babel, it’s loaders and presets to the development dependencies and create a configuration file for it.

npm install --save-dev babel-cli @babel/core babel-loader @babel/preset-env babel-preset-es2015 @babel/preset-react babel-register babel-plugin-transform-class-properties clean-webpack-plugin webpack-cli


touch .babelrc
add add following code in it

{
  "presets": ["@babel/preset-env", "@babel/preset-react"],
  "plugins": ["transform-class-properties"]
}


Now webpack is installed, we need to configure webpack.config.js

Add style loaders:
npm install --save-dev css-loader style-loader sass-loader node-sass


touch webpack.config.js

add following code in this above created file:
const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');

module.exports = {
    entry: path.join(__dirname, 'assets/src/js/index'),
    output: {
        path: path.join(__dirname, 'assets/dist'),
        filename: '[name].js'
    },
    mode: "development",

    // Configurations with webpack 5
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader",
                },
            },
        ],
    },
    optimization: {
        minimize: true,
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify('development')
        }),
        new CleanWebpackPlugin(),
        new BundleTracker({
            path: __dirname,
            filename: 'webpack-stats.json'
        }),
    ],
}

add following code in package.json
"scripts": {
  ...
  "start": "./node_modules/.bin/webpack --config webpack.config.js",
  "watch": "npm run start -- --watch"
},

Now for calling Webpack to compile the files you can run npm run start on a terminal. 
For doing it on watch mode type npm run watch: it will update the results every time a file is changed.



add following in assets/src/js/index.js

import React from 'react';
import ReactDOM from 'react-dom';
class App extends React.Component {
  render () {
    return (
      <h1>Django + React + Webpack + Babel = Awesome App</h1>
    )
  }
}
ReactDOM.render(<App />, document.getElementById('react-app'));


Organizing React APP:

$ mkdir -p assets/src/js/components/Title assets/src/js/containers/App
$ touch assets/src/js/components/Title/index.js assets/src/js/containers/App/index.js

Add following in assets/src/js/components/Title/index.js
import React from 'react';
const Title = ({ text }) => {
  return (
    <h1>{text}</h1>
  )
}
export default Title;

add following in assets/src/js/containers/App/index.js

import React from 'react';
import Title from '../../components/Title';
class App extends React.Component {
  render () {
    const text = 'Django + React + Webpack + Babel = Awesome App';
    return (
      <Title text={text} />
    )
  }
}
export default App;

add following in assets/src/js/index.js

import React from 'react';
import ReactDOM from 'react-dom';
import App from './containers/App';
ReactDOM.render(<App />, document.getElementById('react-app'));



add following in assets/src/scss/index.scss

@import "./title";

add following in assets/src/scss/title.scss

.title {
  color: red;
}

add following in assets/src/js/index.js

import '../scss/index.scss';

add following in assets/src/js/components/Title/index.js

    <h1 className="title">{text}</h1>

/usr/bin/certbot renew --quiet
