'use strict';

var flaskrpg = {

  summernote_init: function() {
    $('.summernote').summernote();
  },
  
  init: function() {
    console.log('flaskrpg.init()...');
    flaskrpg.summernote_init();
    console.log('flaskrpg.init() done');
  },
}

$(document).ready(function() {flaskrpg.init();});
