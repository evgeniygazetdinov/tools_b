var gulp = require('gulp');
var rsync = require('gulp-rsync');



function deploy(done) {
  gulp.src('./*')
    .pipe(rsync({
      root: '',
      hostname: 'root@199.192.21.240',
      destination: '/opt/tools_b-master',
    }))
   done();};


// The default task (called when you run `gulp` from cli) 
gulp.task('default', deploy);