<!-- main Korean sentence parser UI -->

<template>
    <div>
        Hello!!!
        <table v-if="wordList">
            <template v-for="(row, rowIndex) in wordList">
                <tr>
                    <td v-for="cd in row">
                        <span class="index">{{ cd.index }}:</span><span class="word" v-on:click="clickWord(cd, $event)"> {{ cd.word }}</span>
                    </td>
                </tr>
                <tr>
                    <td v-if="selection && selection.row == rowIndex+1" colspan="10" class="def-row">
                        <div v-for="pos in Object.keys(selection.posDefs)">
                            {{ pos }}: {{ selection.posDefs[pos]}}
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
		};
	},

    mounted: function () {
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
            this.selection = this.selection == cd ? null : cd;
        }

    }
}
</script>

<style>

.word {
    cursor: pointer;
}

</style>
