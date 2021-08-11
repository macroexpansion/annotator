<template>
  <div
    class="card"
    v-show="show"
    :style="{
      'border-top': `0.5px solid ${borderColor}`,
      'border-right': `0.5px solid ${borderColor}`,
      'border-bottom': `0.5px solid ${borderColor}`,
      'border-left': `0.5px solid ${borderColor}`,
      'margin-bottom': `4px`
    }"
  >
    <div @click="click" class="card-header" :id="'heading' + category.id">
      <div :style="{ color: textColor , height: '28px'}">
        <div>
          <i
            :style="{ color: (annotateMode === 'annotate' || editMode) ? 'white' : 'darkgray' }"
            class="fa category-icon"
            :class="{'fa-check-square-o': isSelected, 'fa-square-o': !isSelected}"
          />
        </div>

        <span
          class="btn btn-link btn-sm collapsed category-text"
          style="color: inherit"
          aria-expanded="false"
        >
          {{ category.name }}
        </span>
      </div>
    </div>

    <div
      class="card-header"
      v-for="(subcategory, idx) in subcategories"
      :key="idx"
      :style="{ color: subTextColor , height: '28px'}"
      @click="subcategoryClick(idx)"
    >
      <div style="padding-left: 10%">
        <i
          :style="{ color: isSelected && (annotateMode === 'annotate' || editMode) ? 'white' : 'darkgray' }"
          class="fa category-icon"
          :class="{'fa-check-square-o': subcategory.value, 'fa-square-o': !subcategory.value}"
        />
      </div>
      <span
        class="btn btn-link btn-sm collapsed category-text"
        style="color: inherit"
        aria-expanded="false"
      >
        {{ subcategory.name }}
      </span>
    </div>

  </div>
</template>

<script>
import toastrs from "@/mixins/toastrs";

import Annotations from "@/models/annotations";

export default {
  name: "Label",
  mixins: [toastrs],
  model: {
    prop: "categoryIds",
    event: "update"
  },
  props: {
    category: {
      type: Object,
      required: true
    },
    categoryIds: {
      type: Array,
      required: true
    },
    search: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      annotation_id: null,
      subcategories : []
    };
  },
  computed: {
    borderColor() {
      return this.labelIsSelected ? this.category.color : '#404552';
    },
    textColor() {
      if (this.isSelected && (this.annotateMode === 'annotate' || this.editMode))
        return 'rgb(129, 230, 113)';
      else if (this.editMode)
        return 'white';
      else if (this.annotateMode === 'review')
        return 'darkgray';
      else
        return 'white'
    },
    subTextColor() {
      if (this.labelIsSelected)
        return 'white'
      else
        return 'darkgray'
    },
    show() {
      let search = this.search.toLowerCase();
      if (search.length === 0) return true;
      return this.category.name.toLowerCase().includes(search);
    },
    isSelected() {
      return this.categoryIds.indexOf(this.category.id) > -1;
    },
    annotateMode() {
      return this.$store.getters['review/annotateMode'];
    },
    editMode() {
      return this.$parent.edit;
    },
    labelIsSelected() {
      if (this.isSelected && (this.annotateMode === 'annotate' || this.editMode))
        return true;
      return false;
    }
  },
  methods: {
    getSubcategories() {
      for (const subcategory of Array.from(this.category.subcategory)) {
        if (this.category.annotations[0] && this.category.annotations[0].subannotations.length > 0) {
          let exist = false;
          for (const annotation of Array.from(this.category.annotations[0].subannotations)) {
            if (subcategory.name === annotation.name) {
              this.subcategories.push(annotation);
              exist = true;
              break;
            }
          }
          if (!exist) this.subcategories.push({ name: subcategory.name, value: false })
        } else {
          this.subcategories = this.category.subcategory.map(x => ({ name: x.name, value: false }))
        }
      }
    },
    click() {
      if (this.annotateMode === 'annotate' || this.editMode) {
        let copy = this.categoryIds.slice();
        if (!this.isSelected) {
          copy.push(this.category.id);
          this.createAnnotation(true, "create");
        } else {
          copy.splice(copy.indexOf(this.category.id), 1);
          // this.subcategories.forEach(subcategory => {
          //   subcategory.value = false;
          // })
        }
        this.$emit("update", copy);
      }
    },
    subcategoryClick(idx) {
      if (this.labelIsSelected) {
        this.subcategories[idx].value = !this.subcategories[idx].value;
      }
    },
    createAnnotation(label, action) {
      Annotations.createLabel({
        image_id: this.$parent.image.id,
        category_id: this.category.id,
        creator: this.$parent.user
      })
      .then(response => {
        this.annotation_id = response.data.id;
        this.$socket.emit("annotation", {
          action: action,
          category_id: this.category.id,
          annotation: response.data
        });
      })
      .catch(error => {
        this.axiosRequestError('Annotation', 'Create annotation error');
      }) 
    },
    export() {
      let data = {
        id: this.category.id,
        name: this.category.name,
        show: true,
        visualize: false,
        color: this.category.color,
        annotations: [{
          id: this.annotation_id,
          isbbox: false,
          label: this.isSelected,
          subannotations: this.subcategories
        }],
      }

      return data;
    }
  },
  mounted() {
    if (this.category.annotations.length > 0) {
      this.annotation_id = this.category.annotations[0].id;
    }
    this.getSubcategories();
  }
};
</script>

<style scoped>
.list-group-item {
  height: 22px;
  font-size: 13px;
  padding: 2px;
  background-color: #404552;
}

.category-icon {
  display: block;
  float: left;
  margin: 0;
  padding: 5px 10px 5px 10px;
}

.btn-link {
  margin: 0;
  padding: 0;
}

.annotation-icon {
  margin: 0;
  padding: 3px;
}

.card-header {
  display: block;
  margin: 0;
  padding: 0;
}

.card {
  background-color: #4b5162;
}
</style>
