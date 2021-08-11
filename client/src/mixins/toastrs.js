export default {
  methods: {
    axiosRequestError(title, message) {
      let options = {
        progressBar: true,
        positionClass: "toast-bottom-left"
      };

      this.$toastr.error(message, title, options);
    },
    axiosRequestSuccess(title, message) {
      let options = {
        progressBar: true,
        positionClass: "toast-bottom-left"
      };

      this.$toastr.success(message, title, options);
    }
  }
};
