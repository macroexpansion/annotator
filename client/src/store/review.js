export default {
    namespaced: true,
    state: () => ({
        reviewUser: "",
        annotateMode: ""
    }),
    getters: {
        reviewUser(state) {
            return state.reviewUser;
        },
        annotateMode(state) {
            return state.annotateMode;
        }
    },
    mutations: {
        setAnnotateMode(state, mode) {
            state.annotateMode = mode;
        },
        setReviewUser(state, reviewUser) {
            state.reviewUser = reviewUser;
        }
    }
}