<template>
  <div class="upload-file-container">
    <Loading v-if="uploading" />
    <form ref="uploadForm" class="upload-form" @submit.prevent="uploadFiles()">
      <div class="row file-input">
        <input type="file"
               ref="files"
               multiple
               :disabled="uploading"
               @input="onFilesInput" />
      </div>

      <div class="row btn-container">
        <button type="submit" :disabled="uploading || !hasFiles">
          <i class="fa fa-upload" />&nbsp; Upload
        </button>
      </div>
    </form>

    <div class="existing-files-container">
      <ConfirmDialog v-for="file in existingFiles"
                     :key="file.name"
                     :visible="true"
                     @close="delete existingFiles[file.name]"
                     @input="uploadFiles([file], {force: true})">
        The file <b>{{ file.name }}</b> already exists. Do you want to overwrite it?
      </ConfirmDialog>
    </div>

    <div class="progress-container" v-if="Object.keys(progress || {}).length">
      <div class="row progress" v-for="(percent, file) in progress" :key="file">
        <span class="filename">{{ file }}</span>
        <span class="progress-bar-container">
          <progress class="progress-bar" :value="percent" max="100" />
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import Loading from "@/components/Loading";
import Utils from "@/Utils";

export default {
  emits: ['complete', 'error', 'start'],
  mixins: [Utils],
  components: {
    ConfirmDialog,
    Loading,
  },

  props: {
    path: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      existingFiles: {},
      hasFiles: false,
      progress: {},
      uploading: false,
    }
  },

  computed: {
    formFiles() {
      if (!this.$refs.files?.files) {
        return []
      }

      return Array.from(this.$refs.files.files)
    },
  },

  methods: {
    async uploadFile(file, opts) {
      const { force } = opts || {}
      if (force) {
        delete this.existingFiles[file.name]
      }

      try {
        const reqMethod = force ? 'put' : 'post'
        const response = await axios[reqMethod](
          `/file?path=${this.path}/${file.name}`,
          file,
          {
            onUploadProgress: (progressEvent) => {
              this.progress[file.name] = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              )
            },
            headers: {
              'Content-Type': file.type,
            },
          },
        )

        this.notify({
          title: 'File uploaded',
          text: `${file.name} uploaded to ${this.path}`,
          image: {
            icon: 'check',
          },
        })

        return {
          file,
          status: response.status,
        }
      } catch (error) {
        const ret = {
          file,
          status: error.response?.status,
          error: error.response?.data?.error,
        }

        if (ret.status !== 409) {
          this.onUploadError(error)
        }

        return ret
      }
    },

    async uploadFiles(files, opts) {
      const { force } = opts || {}
      files = files || this.formFiles
      files.forEach((file) => {
        delete this.existingFiles[file.name]
      })

      if (!files?.length) {
        this.notify({
          title: 'No files selected',
          text: 'Please select files to upload',
          warning: true,
          image: {
            icon: 'upload',
          },
        })
        return
      }

      this.onUploadStarted(files)
      const failed = []

      try {
        const responses = await Promise.all(
          files.map((file) => this.uploadFile(file, { force }))
        )

        failed.push(...responses.filter((r) => r?.error))
        if (!failed.length) {
          this.onUploadCompleted()
        }
      } finally {
        this.uploading = false
      }

      const conflicts = failed.filter((r) => r?.status === 409 && r?.error)
      this.existingFiles = {
        ...this.existingFiles,
        ...conflicts.reduce((acc, r) => {
          acc[r.file.name] = r.file
          return acc
        }, {}),
      }
    },

    onFilesInput(event) {
      this.hasFiles = Array.from(event.target.files).length > 0
    },

    onUploadStarted(files) {
      this.uploading = true
      this.$emit('start')
      this.notify({
        title: 'Upload started',
        text: `Uploading ${files.length} file(s) to ${this.path}`,
        image: {
          icon: 'upload',
        },
      })
    },

    onUploadCompleted() {
      this.uploading = false
      this.$emit('complete')
    },

    onUploadError(error) {
      const details = error.response?.data?.error
      if (details) {
        error.message = `${error.message}: ${details}`
      }

      this.$emit('error', error)
      this.notify({
        title: 'Upload error',
        text: error.message,
        error: true,
        image: {
          icon: 'upload',
        },
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.upload-file-container {
  :deep(.modal) {
    .modal-body {
      position: relative;
    }
  }

  form {
    .row {
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 1em 0;
    }
  }

  .progress-container {
    display: flex;
    flex-direction: column;

    .progress {
      width: 100%;
      display: flex;
      align-items: center;
      padding: 1em;

      .filename {
        width: 35%;
        overflow: clip;
        text-overflow: ellipsis;
      }

      .progress-bar-container {
        width: 65%;
      }

      progress[value] {
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        border: none;
        width: 100%;
        height: 1.5em;
        border-radius: 0.75em;
      }
    }
  }
}
</style>
