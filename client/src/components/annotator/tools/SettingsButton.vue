<template>
  <div>
    <i
      v-tooltip.right="name"
      class="fa fa-lg fa-cog"
      style="color: white"
      data-toggle="modal"
      data-target="#settings"
    ></i>
    <p class='text-wrap' :style="{ color: 'white', 'font-size': '13px' }">
      {{ name }}
    </p>
    
    <!-- Modal -->
    <div
      class="modal fade"
      id="settings"
      tabindex="-1"
      role="dialog"
      aria-labelledby="settingsLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="settingsLabel">Keyboard Shortcuts</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <!-- <div class="form-group row">
              <label class="col-sm-2 col-form-label">Simplify</label>
              <div class="col-sm-9">
                <input
                  v-model.number="$parent.simplify"
                  type="number"
                  class="form-control"
                />
              </div>
            </div> -->

            <!-- <div class="form-group row">
              <label class="col-sm-2 col-form-label">Annotate API</label>
              <div class="col-sm-9">
                <input
                  type="string"
                  v-model.number="$parent.dataset.annotate_url"
                  class="form-control"
                />
              </div>
            </div> -->

            <Metadata v-show="false" :metadata="metadata" ref="metadata" />

            <!-- <p style="margin: 5px 0 0 0">Keyboard Shortcuts</p> -->

            <div class="row">
              <div class="col-sm">
                <p class="title">Operation</p>
              </div>
              <div class="col-sm">
                <p class="title">Shortcut</p>
              </div>
            </div>

            <ul class="list-group" style="height: 50%;">
              <CustomShortcut
                class="subtitle"
                v-for="(command, index) in commands"
                :key="index"
                :shortcut="command"
                ref="shortcuts"
              />
            </ul>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-dismiss="modal"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Metadata from "@/components/Metadata";
import CustomShortcut from "@/components/annotator/CustomShortcut";

export default {
  name: "SettingsButton",
  components: { CustomShortcut, Metadata },
  props: {
    metadata: {
      type: Object,
      required: true
    },
    commands: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      name: "Shortcuts"
    };
  },
  methods: {
    exportMetadata() {
      return this.$refs.metadata.export();
    },
    export() {
      let data = { shortcuts: [] };
      this.$refs.shortcuts.forEach(shortcut => {
        data.shortcuts.push(shortcut.export());
      });
      return data;
    }
  }
};
</script>

<style scoped>
.subtitle {
  margin: 1;
  font-size: 15px;
}

.title {
  margin: 4;
  font-size: 20px;
}
</style>
