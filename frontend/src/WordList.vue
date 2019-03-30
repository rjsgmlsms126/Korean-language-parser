<!-- main Korean sentence parser UI -->

<template>
    <div>
        <table v-if="wordList">
            <template v-for="(row, rowIndex) in wordList">
                <tr>
                    <td v-for="cd in row">
                        <span class="index">{{ cd.index }}:</span><span class="word" v-on:click="clickWord(cd, $event)"> {{ cd.word }}</span>
                    </td>
                </tr>
                <tr>
                    <td v-if="selection && selection.row == rowIndex+1" colspan="10" class="definition-row">
                        <div v-for="pos in selection.posDefs" class="definition">
                            <div v-if="pos.pos != 'unknown' || selection.posDefs.length == 1" class="def-div">
                                <span class="pos">{{ pos.pos }}:</span><span class="pos-definition"> {{ pos.defStr }}</span>
                            </div>
                            <div v-for="sample in pos.samples">
                                <span class="sample-korean">{{ sample.k }}</span><span class="sample-english">{{ sample.e }}</span>
                            </div>
                        </div>
                    </td>
                </tr>
            </template>
        </table>
    </div>
</template>

<script>
export default {
    name: 'WordList',

    // ------------ component local data ------------
	data: function() {
		return {
		    APIHost: "http://localhost:9000", // "http://localhost:9000", // ""
            wordList: null,
            selection: null,
            selectedCell: null
		};
	},

    mounted: function () {
        this.createClasses();
        this.getWordList();
    },

	computed: {
	},

    // ---------- component methods ---------

	methods: {

        getWordList: function() {
            // call word-list getter API
            var self = this;
            $.ajax({
                method: "GET",
                url: self.APIHost + "/get-word-list/", // http://localhost:9000
                crossDomain: true,
                success: function (response) {
                    if (response.result == "OK")
                        self.wordList = response.wordList;
                }
            });
        },

        clickWord: function(cd, event) {
            // handle click on a word
            var el = $(event.target);
            if (this.selectedCell)
                this.selectedCell.removeClass("selected-word");
            if (this.selection == cd) {
                // toggling off
                this.selection = this.selectedCell = null;
            }
            else {
                // select & highlight word
                this.selection = cd;
                el.addClass("selected-word");
                this.selectedCell = el;
                // compute offset for definition
                var d = $($(".definition")[0]),
                    wordStart = el.position().left,
                    wordCenter = wordStart + el.outerWidth() / 2,
                    left = Math.min(Math.max(15, wordStart - 30), $('body').outerWidth() - 700); //wordCenter - d.outerWidth() / 2;
                this.definitionClass.innerHTML = ".definition { display: inline; position: relative; left: " + left + "px; }";
            }
        },

        createClasses: function() {
            // create classes to be dynamically modified
            var css = document.createElement("style");
            css.type = "text/css";
            css.innerHTML = ".definition { display: inline; position: relative; }";
            document.body.appendChild(css);
            this.definitionClass = css;
        }

    }
}
</script>

<style>

    .index {
        color: #a05252;;
        font-size: 80%;
        width: 50px;
    }

    .word {
        cursor: pointer;
        margin-left: 2px;
    }

    .selected-word {
        background-color: #f7d4cd;
        border: thin grey solid;
        border-radius: 3px;
        padding: 2px;
    }
    
    .definition-row {
        /* text-align: center; */
        padding-top: 4px;
        padding-bottom: 4px;
    }

    .def-div {
        display: block;
        padding-top: 2px;
        padding-bottom: 6px;
    }

    .pos {
        color: #003eff;
    }

    .pos-definition {
        color: rgb(79, 120, 156);
    }

    .sample-korean {
        color: #454545;
        padding-left: 10px;
        padding-right: 12px;
    }

    .sample-english {
        color: rgb(79, 120, 156);
    }

</style>
