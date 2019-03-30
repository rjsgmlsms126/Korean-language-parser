// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import KoreanParser from './KoreanParser'
import WordList from './WordList'

Vue.config.productionTip = false

/* eslint-disable no-new */
// new Vue({
//   el: '#korean-parser',
//   components: { KoreanParser, },
//   template: '<KoreanParser/>'
// })

window.vm = new Vue({
    el: '#body',
    components: { KoreanParser, WordList, },
	data: function() {
        return {
            app: window.app,  // selected by index.html template rendering
        }
    }
})
