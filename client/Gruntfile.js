module.exports = function(grunt) {
  'use strict';
  //
  // Grunt configuration:
  //
  grunt.initConfig({
    manifest:{
      dest: 'tmp/'
    },

    lint: {
      files: ['Gruntfile.js', 'app/scripts/**/*.js'],
    },

    jshint: {
      all: ['Gruntfile.js', 'app/scripts/**/*.js'],
      options: {
        curly: true,
        eqeqeq: true,
        immed: true,
        latedef: true,
        newcap: true,
        noarg: true,
        sub: true,
        undef: true,
        boss: true,
        eqnull: true,
        browser: true
      },
      globals: {
        angular: true
      }
    },

    clean: {
      release: ['tmp']
    },

    copy: {
        release: {
            files: [{
              dest: 'tmp/', cwd: 'app/', src: ['**'], expand: true
            }]
        }
    },

    // usemin handler should point to the file containing
    // the usemin blocks to be parsed
    'useminPrepare': {
      html: ['tmp/index.html',
             'tmp/globaleaks.html',
      ],
      options: {
        dest: 'tmp'
      }
    },

    // update references in HTML/CSS
    usemin: {
      html: ['tmp/views/**/*.html',
             'tmp/index.html',
      ],
      options: {
        dirs: ['tmp']
      }
    },

    cssmin: {
      combine: {
        files: {
          'tmp/styles-rtl.css': [ 'tmp/components/bootstrap-rtl/dist/css/bootstrap-rtl.css',
                                  'tmp/components/jquery-file-upload/css/jquery.fileupload.css',
                                  'tmp/components/jquery-file-upload/css/jquery.fileupload-ui.css',
                                  'tmp/styles/main.css',
                                  'tmp/styles/admin.css',
                                  'tmp/styles/home.css',
                                  'tmp/styles/submission.css']
        }
      }
    },

    // HTML minification
    html: {
      files: ['**/*.html']
    },

    // Put all angular.js templates into a single file
    ngtemplates:  {
      GLClient: {
            cwd: 'app',
            options: {base: 'app/'},
            src: ['views/**/*.html'],
            dest: 'tmp/scripts/templates.js'
          }
    },

    lineremover: {
      customExclude: {
        files: {
          'tmp/index.html': 'tmp/index.html'
        },
        options: {
          exclusionPattern: /<link rel="stylesheet" href="(styles|styles-rtl)\.css"\/>/g
        }
      },
    },

   'string-replace': {
      inline: {
        files: {
          'tmp/index.html': 'tmp/index.html',
        },
        options: {
          replacements: [
            {
              pattern: '<script src="scripts.js"></script>',
              replacement: ''
            },
            {
              pattern: '<!-- start_globaleaks(); -->',
              replacement: 'start_globaleaks();'
            }
          ]
        }
      }
    },

    karma: {
      unit: {
        configFile: 'karma.conf.js'
      }
    },

    coveralls: {
      options: {
            debug: true,
            coverage_dir: 'coverage'
      }
    },

    confirm: {
      updateTranslations: {
        options: {
          // Static text.
          question: 'WARNING:\n'+
                    'this task may cause translations loss and should be executed only on master branch.\n\n' +
                    'Are you sure you want to proceed (Y/N)?',
          continue: function(answer) {
            return answer === 'Y';
          }
        }
      }
    },

  });

  // Prefer explicit to loadNpmTasks to:
  //   require('matchdep').filterDev('grunt-*').forEach(grunt.loadNpmTasks);
  //
  // the reasons is during time strangely the automating loading was causing problems.
  grunt.loadNpmTasks('grunt-angular-templates');
  grunt.loadNpmTasks('grunt-confirm');
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-line-remover');
  grunt.loadNpmTasks('grunt-manifest');
  grunt.loadNpmTasks('grunt-string-replace');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-usemin');
  grunt.loadNpmTasks('grunt-karma');
  grunt.loadNpmTasks('grunt-karma-coveralls');

  var path = require('path'),
    superagent = require('superagent'),
    fs = require('fs'),
    Gettext = require("node-gettext")

  grunt.registerTask('cleanupWorkingDirectory', function() {
    var rm_rf = function(dir) {
      var s = fs.statSync(dir);

      if (!s.isDirectory()) {return fs.unlinkSync(dir);}

      fs.readdirSync(dir).forEach(function(f) {
        rm_rf(path.join(dir || '', f || ''))
      });

      fs.rmdirSync(dir);
    };


    grunt.file.mkdir('build/');

    var files = ['globaleaks.html', 'index.html', 'loader.js', 'styles.css', 'styles-rtl.css', 'scripts.js']
    for (var x in files) {
        grunt.file.copy('tmp/' + files[x], 'build/' + files[x])
    }

    var dirs = ['data', 'fonts', 'img', 'l10n']
    for (var x in dirs) {
      grunt.file.mkdir(dirs[x]);
      grunt.file.recurse('tmp/' + dirs[x], function(absdir, rootdir, subdir, filename) {
        grunt.file.copy(absdir, path.join('build/' + dirs[x], subdir || '', filename || ''));
      });
    }

    rm_rf('tmp');
  });

  function str_escape (val) {
      if (typeof(val)!="string") return val;
      return val      
        .replace(/[\n]/g, '\\n')
        .replace(/[\t]/g, '\\r');
  }

  function str_unescape (val) {
      if (typeof(val)!="string") return val;
      return val
        .replace(/\\n/g, '\n')
        .replace(/\\t/g, '\t');
  }

  function readTransifexrc(){
    var transifexrc = fs.realpathSync(process.env.HOME + '/.transifexrc'),
      err = fs.stat(transifexrc),
      usernameRegexp = /username = (.*)/,
      passwordRegexp = /password = (.*)/,
      content, login = {};

    if (err) {
      console.log(transifexrc + " does not exist");
      console.log("It should contain");
      console.log("username = <your username>");
      console.log("password = <your password>");
      throw 'No transifexrc file';
    }

    content = grunt.file.read(transifexrc);
    login.username = usernameRegexp.exec(content)[1];
    login.password = passwordRegexp.exec(content)[1];
    return login;
  }

  var agent = superagent.agent(),
    baseurl = 'http://www.transifex.com/api/2/project/globaleaks',
    sourceFile = 'pot/en.po';

  function fetchTxSource(cb){
    var url = baseurl + '/resource/master/content',
      login = readTransifexrc();

    agent.get(url)
      .auth(login.username, login.password)
      .end(function(err, res){
        if (res.ok) {
          var content = JSON.parse(res.text)['content'];
          fs.writeFileSync(sourceFile, content);
          console.log("Written source to " + sourceFile + ".");
          cb();
        } else {
          console.log('Error: ' + res.text);
        }
    });
  }

  function updateTxSource(cb){
    var url = baseurl + '/resource/master/content/',
      content = grunt.file.read(sourceFile),
      login = readTransifexrc();

    agent.put(url)
      .auth(login.username, login.password)
      .set('Content-Type', 'application/json')
      .send({'content': content})
      .end(function(err, res){
        if (res.ok) {
          cb();
        } else {
          console.log('Error: ' + res.text);
        }
    });
  }

  function listLanguages(cb){
    var url = baseurl + '/resource/master/?details',
      login = readTransifexrc();

    agent.get(url)
      .auth(login.username, login.password)
      .end(function(err, res){
        if (res.ok) {
          var result = JSON.parse(res.text);
          cb(result);
        } else {
          console.log('Error: ' + res.text);
        }
    });

  }

  function fetchTxTranslationsForLanguage(langCode, cb) {
    var resourceUrl = baseurl + '/resource/master/',
      login = readTransifexrc();

    agent.get(resourceUrl + 'stats/' + langCode + '/')
      .auth(login.username, login.password)
      .end(function(err, res){
        if (res.ok) {
          var content = JSON.parse(res.text);

          if (content.translated_entities > content.untranslated_entities) {
            agent.get(resourceUrl + 'translation/' + langCode + '/')
              .auth(login.username, login.password)
              .end(function(err, res){
                if (res.ok) {
                  var content = JSON.parse(res.text)['content'];
                  cb(content);
                } else {
                  console.log('Error: ' + res.text);
                }
            });
          } else {
            cb();
          }
        } else {
          console.log('Error: ' + res.text);
        }
      })
  }

  function fetchTxTranslations(cb){
    var fetched_languages = 0,
      total_languages, supported_languages = {};

    listLanguages(function(result){
      result.available_languages = result.available_languages.filter(function( language ) {
        /*
            we skip en_US that is used internaly only as feedback in order
            to keep track of corrections suggestions
        */
        return language.code !== 'en_US';
      });

      total_languages = result.available_languages.length;

      result.available_languages.forEach(function(language){

        var content = grunt.file.read(sourceFile);

        fetchTxTranslationsForLanguage(language.code, function(content){
          if (content) {
            var potFile = "pot/" + language.code + ".po";

            fs.writeFileSync(potFile, content);
            console.log("Fetched " + language.code);
            supported_languages[language.code] = language.name;
          }

          fetched_languages += 1;

          if (total_languages == fetched_languages) {
            var sorted_keys = Object.keys(supported_languages).sort();

            console.log("List of available translations:");

            for (var i in sorted_keys) {
              console.log(" { \"code\": \"" + sorted_keys[i] +
                          "\", \"name\": \"" + supported_languages[sorted_keys[i]] +"\" },");
            }

            cb(supported_languages);
          }
        });

      });
    });
  }

  grunt.registerTask('updateTranslationsSource', function() {

    var done = this.async(),
      gt = new Gettext(),
      strings,
      translations = {},
      translationStringRegexpHTML1 = /"(.+?)"\s+\|\s+translate/gi,
      translationStringRegexpHTML2 = /translate>(.+?)</gi,
      translationStringRegexpJSON = /"en": "(.+)"/gi,
      translationStringCount = 0;

    gt.addTextdomain("en");

    function extractPotFromHTMLFile(filepath) {
      var filecontent = grunt.file.read(filepath),
        result;

      while ( (result = translationStringRegexpHTML1.exec(filecontent)) ) {
        gt.setTranslation("en", "", result[1], result[1]);
        translationStringCount += 1;
      }

      while ( (result = translationStringRegexpHTML2.exec(filecontent)) ) {
        gt.setTranslation("en", "", result[1], result[1]);
        translationStringCount += 1;
      }

    };

    function extractPotFromJSONFile(filepath) {
      var filecontent = grunt.file.read(filepath),
        result;

      while ( (result = translationStringRegexpJSON.exec(filecontent)) ) {
        gt.setTranslation("en", "", result[1], result[1]);
        translationStringCount += 1;
      }
    };

    function extractPotFromTXTFile(filepath) {
      var filecontent = grunt.file.read(filepath),
          lines = filecontent.split("\n"),
          result;

      for (var i=0; i<lines.length; i++){

        // we skip adding empty strings and variable only strings
        if (lines[i] != '' && !lines[i].match(/^%[a-zA-Z0-9]+%/g)) {
          gt.setTranslation("en", "", lines[i], lines[i]);
          translationStringCount += 1;
        }
      }
    };

    extractPotFromHTMLFile('app/globaleaks.html');

    /* Extract strings view file used to anticipate strings on transifex */
    extractPotFromHTMLFile('app/translations.html');

    grunt.file.recurse('app/views/', function(absdir, rootdir, subdir, filename) {
      var filepath = path.join('app/views/', subdir || '', filename || '');
      extractPotFromHTMLFile(filepath);
    });

    grunt.file.recurse('app/data/txt', function(absdir, rootdir, subdir, filename) {
      var filepath = path.join('app/data/txt', subdir || '', filename || '');
      extractPotFromTXTFile(filepath);
    });

    extractPotFromJSONFile('app/data/appdata.json')

    grunt.file.mkdir("pot");

    fs.writeFileSync("pot/en.po", gt.compilePO("en"));

    console.log("Written " + translationStringCount + " string to pot/en.po.");

    updateTxSource(done);

  });

  grunt.registerTask('makeTranslations', function() {

    var done = this.async(),
      gt = new Gettext(),
      strings,
      fileContents = fs.readFileSync("pot/en.po");

    fetchTxTranslations(function(supported_languages){

      gt.addTextdomain("en", fileContents);
      strings = gt.listKeys("en", "");

      for (var lang_code in supported_languages) {

        var translations = {},
          output;

        strings.forEach(function(string){

          gt.addTextdomain(lang_code, fs.readFileSync("pot/" + lang_code + ".po"));
          translations[string] = str_unescape(gt.dgettext(lang_code, str_escape(string)));

        });

        output = JSON.stringify(translations);

        fs.writeFileSync("app/l10n/" + lang_code + ".json", output);

      }

      done();

    });

  });

  grunt.registerTask('makeAppData', function() {

    var done = this.async(),
      gt = new Gettext(),
      strings,
      fileContents = fs.readFileSync("pot/en.po");

    fetchTxTranslations(function(supported_languages){
      gt.addTextdomain("en", fileContents);

      for (var lang_code in supported_languages) {
        gt.addTextdomain(lang_code, fs.readFileSync("pot/" + lang_code + ".po"));
      }

      var json = JSON.parse(fs.readFileSync("app/data/appdata.json")),
          output = {},
          version = json['version'],
          fields = json['fields'],
          templates = json['templates'],
          templates_sources = {};

      grunt.file.recurse('app/data/txt', function(absdir, rootdir, subdir, filename) {
        var template_name = filename.split('.txt')[0],
            filepath = path.join('app/data/txt', subdir || '', filename || ''),
            result;

        templates_sources[template_name] = grunt.file.read(filepath);

      });

      for (var lang_code in supported_languages) {

        for (var template_name in templates_sources) {
          
          if (!(template_name in templates)) {
            templates[template_name] = {}
          }

          var tmp = templates_sources[template_name];

          var lines = templates_sources[template_name].split("\n");

          for (var i=0; i<lines.length; i++){

            // we skip adding empty strings and variable only strings
            if (lines[i] != '' && !lines[i].match(/^%[a-zA-Z0-9]+%/g)) {
              tmp = tmp.replace(lines[i], str_unescape(gt.dgettext(lang_code, str_escape(lines[i]))));
            }
          }

          templates[template_name][lang_code] = tmp;

        }

      }

      output['version'] = version;
      output['fields'] = fields;
      output['templates'] = templates;

      output['node'] = {};

      for (var k in json['node']){

        output['node'][k] = {};
        for (var lang_code in supported_languages) {
          output['node'][k][lang_code] = str_unescape(gt.dgettext(lang_code, str_escape(json['node'][k]['en'])));

        }
      }

      var tos_translate = function(option) {
        var keys = ['clause', 'agreement_statement']
        for (var k in keys){

          for (var lang_code in supported_languages) {
            option['attrs'][keys[k]][lang_code] = str_unescape(gt.dgettext(lang_code, str_escape(option['attrs'][keys[k]]['en'])));
          }
        }
      }

      var field_translate = function(field) {
        var keys = ['label', 'description', 'hint']
        for (var k in keys){

          for (var lang_code in supported_languages) {
            field[keys[k]][lang_code] = str_unescape(gt.dgettext(lang_code, str_escape(field[keys[k]]['en'])));
          }

        }

        for (var c in field['children']){
          field_translate(field['children'][c]);
        }

        if (field['type'] == 'tos') {
          tos_translate(field['options'][0]);
        }
      }

      for (var f in output['fields']){
          field_translate(output['fields'][f]);
      }

      output = JSON.stringify(output);

      fs.writeFileSync("app/data/appdata_l10n.json", output);

      console.log("Fields file was written!");

      done();

    });

  });

  // Run this task to update translation related files
  grunt.registerTask('updateTranslations', ['confirm', 'updateTranslationsSource', 'makeTranslations', 'makeAppData']);

  // Run this to build your app. You should have run updateTranslations before you do so, if you have changed something in your translations.
  grunt.registerTask('build',
    ['clean', 'copy', 'ngtemplates', 'useminPrepare', 'concat', 'cssmin', 'usemin', 'uglify', 'string-replace', 'lineremover', 'manifest', 'cleanupWorkingDirectory']);

  grunt.registerTask('unittest',
    ['build', 'karma', 'coveralls']);

};
