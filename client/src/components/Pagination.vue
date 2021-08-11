<template>
  <div class="row align-items-center justify-content-center bg-light">
    <ul class="pagination text-center">
      <li
        :class="{ 'page-item': true, disabled: page == 1 }"
        @click="previousPage"
      >
        <a class="page-link" aria-label="Previous">
          <span aria-hidden="true">&laquo;</span>
          <span class="sr-only">Previous</span>
        </a>
      </li>
      <li
        v-for="pageIndex in range"
        :key="pageIndex"
        :class="{ 'page-item': true, active: pageIndex + startPage == page }"
      >
        <a class="page-link" @click="page = pageIndex + startPage">{{
          pageIndex + startPage
        }}</a>
      </li>
      <li
        :class="{ 'page-item': true, disabled: page == numPages }"
        @click="nextPage"
      >
        <a class="page-link" aria-label="Next">
          <span aria-hidden="true">&raquo;</span>
          <span class="sr-only">Next</span>
        </a>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "Pagination",
  props: {
    numPages: {
      type: Number,
      required: true,
    },
    datasetPagination: {
      type: Boolean,
      required: false,
    },
    annotatedProp: {
      required: false,
    },
    notAnnotatedProp: {
      required: false,
    },
  },
  data() {
    return {
      range: 20,
      page: 1,
      timer: null,
    };
  },
  methods: {
    previousPage() {
      this.page -= 1;
      if (this.page < 1) {
        this.page = 1;
      }
    },
    nextPage() {
      this.page += 1;
      if (this.page > this.numPages) {
        this.page = this.numPages;
      }
    },
  },
  watch: {
    numPages() {
      if (this.numPages < 20) {
        this.range = this.numPages;
      } else {
        this.range = 20;
      }
    },
    page(newPage, oldPage) {
      if (this.datasetPagination) {
        localStorage.setItem("pagination/page", this.page);
      }

      if (newPage === oldPage) return;

      clearTimeout(this.timer);
      this.timer = setTimeout(() => this.$emit("pagechange", this.page), 0);
    },
    annotatedProp() {
      this.page = parseInt(localStorage.getItem("pagination/page")) || 1;
    },
    notAnnotatedProp() {
      this.page = parseInt(localStorage.getItem("pagination/page")) || 1;
    },
  },
  computed: {
    startPage() {
      if (this.range > this.numPages) {
        return 0;
      }

      let range = Math.round(this.range / 2);
      let start = this.page - range;

      if (start < 0) return 0;

      if (start > this.numPages || start + this.range > this.numPages) {
        return this.numPages - this.range;
      }

      return start;
    },
  },
  created() {
    if (this.range > this.numPages) this.range = this.numPages;
    if (this.datasetPagination) {
      const page = localStorage.getItem("pagination/page");
      if (page != null) {
        this.page = parseInt(page);
      }
    }
  },
};
</script>

<style>
.page {
  display: block;
  margin: 0 auto;
}
</style>
