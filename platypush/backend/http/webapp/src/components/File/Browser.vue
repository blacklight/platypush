<template>
  <div class="browser">
    <Loading v-if="loading" />

    <div class="nav" ref="nav">
      <div class="path-container">
        <span class="path" v-if="hasHomepage">
          <span class="token" @click="path = null">
            <i class="fa fa-home" />
          </span>

          <span class="separator" v-if="pathTokens.length">
            <i class="fa fa-chevron-right" />
          </span>
        </span>

        <span class="path"
              v-for="(token, i) in pathTokens"
              :key="i"
              @click="path = pathTokens.slice(0, i + 1).join('/').slice(1)">
          <span class="token">
            {{ token }}
          </span>

          <span class="separator"
                v-if="(i > 0 || pathTokens.length > 1) && i < pathTokens.length - 1">
            <i class="fa fa-chevron-right" />
          </span>
        </span>
      </div>

      <div class="btn-container">
        <Dropdown :style="{'min-width': '11em'}">
          <DropdownItem icon-class="fa fa-plus" text="New Folder" @input="showCreateDirectory = true" />
          <DropdownItem icon-class="fa fa-file" text="Create File" @input="showCreateFile = true" />
          <DropdownItem icon-class="fa fa-upload" text="Upload" @input="showUpload = true" />
          <DropdownItem icon-class="fa fa-sync" text="Refresh" @input="refresh" />
          <DropdownItem icon-class="fa fa-cog" text="Options" @input="showOptions = true" />
        </Dropdown>
      </div>
    </div>

    <Home :items="homepage"
          :filter="filter"
          :has-back="hasBack"
          @back="onBack"
          @input="onItemSelect"
          v-if="!path && hasHomepage" />

    <div class="items" ref="items" v-else>
      <div class="row item"
           @click="onBack"
           v-if="(path?.length && path !== '/') || hasBack">
        <div class="col-10 left side">
          <i class="icon fa fa-folder" />
          <span class="name">..</span>
        </div>
      </div>

      <div class="row item"
           ref="selectCurrent"
           @click="onSelectCurrentDirectory"
           v-if="hasSelectCurrentDirectory">
        <div class="col-10 left side">
          <i class="icon fa fa-hand-point-right" />
          <span class="name">&lt;Select This Directory&gt;</span>
        </div>
      </div>

      <div class="row item" v-for="(file, i) in filteredFiles" :key="i" @click="onItemSelect(file)">
        <div class="col-10">
          <i class="icon fa" :class="fileIcons[file.path]" />
          <span class="name">
            {{ file.name }}
          </span>
        </div>

        <div class="col-2 actions" v-if="Object.keys(fileActions[file.path] || {})?.length">
          <Dropdown :style="{'min-width': '11em'}">
            <DropdownItem
                v-for="(action, key) in fileActions[file.path]"
                :key="key"
                :icon-class="action.iconClass"
                :text="action.text"
                @input="action.onClick(file)"
            />
          </Dropdown>
        </div>
      </div>
    </div>

    <Modal title="Options"
           :visible="showOptions"
           @close="showOptions = false">
      <div class="modal-body">
        <BrowserOptions :value="opts" @input="onOptsChange" />
      </div>
    </Modal>

    <div class="upload-file-container" v-if="showUpload">
      <FileUploader :path="path"
                    :visible="showUpload"
                    ref="uploader"
                    @complete="onUploadCompleted"
                    @close="showUpload = false" />
    </div>

    <div class="info-modal-container" v-if="showInfoFile != null">
      <Modal title="File Info"
             :visible="showInfoFile != null"
             @close="showInfoFile = null">
        <div class="modal-body">
          <FileInfo :file="showInfoFile" :loading="loading" />
        </div>
      </Modal>
    </div>

    <ConfirmDialog :visible="editWarnings.length > 0"
                   @close="clearEditFile"
                   @input="editFile(editedFile, {force: true})">
      The following warnings were raised:

      <ul>
        <li v-for="(warning, i) in editWarnings" :key="i">
          {{ warning }}
        </li>
      </ul>

      Are you sure you that you want to edit the file?
    </ConfirmDialog>

    <ConfirmDialog :visible="fileToRemove != null"
                   @close="fileToRemove = null"
                   @input="deleteFile(fileToRemove)">
      Are you sure you that you want to delete this file?<br/><br/>
      <b>{{ fileToRemove }}</b>
    </ConfirmDialog>

    <ConfirmDialog :visible="directoryToRemove != null"
                   @close="directoryToRemove = null"
                   @input="deleteDirectory(directoryToRemove)">
      Are you sure you that you want to delete this directory?<br/><br/>
      <b>{{ directoryToRemove }}</b>
    </ConfirmDialog>

    <ConfirmDialog :visible="directoryToRemove != null && directoryNotEmpty"
                   @close="directoryToRemove = null; directoryNotEmpty = false"
                   @input="deleteDirectory(directoryToRemove, {recursive: true})">
      This directory is not empty. Are you sure you that you want to delete it?<br/><br/>
      <b>{{ directoryToRemove }}</b>
    </ConfirmDialog>

    <FileEditor :file="editedFile"
                :is-new="isNewFileEdit"
                :visible="editedFile != null"
                :uppercase="false"
                @close="clearEditFile"
                @save="refresh"
                v-if="editedFile && !editWarnings?.length" />

    <TextPrompt :visible="showCreateDirectory"
                @input="createDirectory($event)"
                @close="showCreateDirectory = false" >
      Enter the name of the new directory:
    </TextPrompt>

    <TextPrompt :visible="showCreateFile"
                @input="editNewFile"
                @close="showCreateFile = false" >
      Enter the name of the new file:
    </TextPrompt>

    <TextPrompt :visible="fileToRename != null"
                :value="displayedFileToRename"
                @input="renameFile"
                @close="fileToRename = null">
      Enter a new name for this file:<br/><br/>
      <b>{{ fileToRename }}</b>
    </TextPrompt>

    <div class="copy-modal-container">
      <Modal :title="(copyFile != null ? 'Copy' : 'Move') + ' File'"
             :visible="showCopyModal"
             @close="showCopyModal = false"
             v-if="showCopyModal">
        <div class="modal-body">
          <Browser :path="path"
                   :has-back="true"
                   :has-select-current-directory="true"
                   :show-directories="true"
                   :show-files="false"
                   @back="copyFile = null; moveFile = null"
                   @input="copyOrMove" />
        </div>
      </Modal>
    </div>
  </div>
</template>

<script>
import BrowserOptions from "./Browser/Options";
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import FileEditor from "./EditorModal";
import FileInfo from "./Info";
import FileUploader from "./UploaderModal";
import Home from "./Home";
import Loading from "@/components/Loading";
import MediaUtils from "@/components/Media/Utils";
import Modal from "@/components/Modal";
import TextPrompt from "@/components/elements/TextPrompt"
import Utils from "@/Utils";

export default {
  emits: [
    'back',
    'input',
    'path-change',
    'play',
  ],
  mixins: [Utils, MediaUtils],
  components: {
    BrowserOptions,
    ConfirmDialog,
    DropdownItem,
    Dropdown,
    FileEditor,
    FileInfo,
    FileUploader,
    Home,
    Loading,
    Modal,
    TextPrompt,
  },

  props: {
    hasBack: {
      type: Boolean,
      default: false,
    },

    hasSelectCurrentDirectory: {
      type: Boolean,
      default: false,
    },

    initialPath: {
      type: String,
    },

    isMedia: {
      type: Boolean,
    },

    filter: {
      type: String,
      default: '',
    },

    filterTypes: {
      type: Array,
      default: () => [],
    },

    homepage: {
      type: Object,
    },

    showDirectories: {
      type: Boolean,
      default: true,
    },

    showFiles: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      copyFile: null,
      directoryNotEmpty: false,
      directoryToRemove: null,
      editedFile: null,
      editWarnings: [],
      files: [],
      fileToRemove: null,
      fileToRename: null,
      info: {},
      isNewFileEdit: false,
      loading: false,
      mimeTypes: {},
      moveFile: null,
      opts: {
        showHidden: false,
        sortBy: 'name',
        reverseSort: false,
      },
      path: this.initialPath,
      showCreateDirectory: false,
      showCreateFile: false,
      showInfoFile: null,
      showOptions: false,
      showUpload: false,
      uploading: false,
    }
  },

  computed: {
    displayedFileToRename() {
      return this.fileToRename?.slice(this.path.length + 1) || ''
    },

    editedFileName() {
      return this.editedFile?.split('/').pop() || 'Untitled'
    },

    filteredTypesMap() {
      return this.filterTypes.reduce((obj, type) => {
        obj[type] = true
        type.split('/').forEach((part) => {
          obj[part] = true
        })

        return obj
      }, {})
    },

    filteredFiles() {
      return this.files.filter(
        file => {
          if (file.type === 'directory' && !this.showDirectories)
            return false
          if (file.type !== 'directory' && !this.showFiles)
            return false
          if ((file?.name || '').toLowerCase().indexOf(this.filter.toLowerCase()) < 0)
            return false
          if (!this.opts.showHidden && file.name.startsWith('.'))
            return false

          if (this.filterTypes.length) {
            const mime = this.mimeTypes[file.path] || ''
            const tokens = [mime, ...mime.split('/')]

            if (!tokens.some((token) => this.fileredTypesMap[token]))
              return false
          }

          return true
        }
      )
    },

    fileActions() {
      return this.files.reduce((obj, file) => {
        const mime = this.mimeTypes[file.path] || ''
        obj[file.path] = {}

        if (this.isMedia && (mime.startsWith('audio/') || mime.startsWith('video/')))
          obj[file.path] = {
            play: {
              iconClass: 'fa fa-play',
              text: 'Play',
              onClick: (file) => this.$emit('play', {type: 'file', url: `file://${file.path}`}),
            },
          }

        if (file.type !== 'directory') {
          obj[file.path].view = {
            iconClass: 'fa fa-eye',
            text: 'View',
            onClick: (file) => this.viewFile(file.path),
          }

          obj[file.path].download = {
            iconClass: 'fa fa-download',
            text: 'Download',
            onClick: (file) => this.downloadFile(file.path),
          }

          obj[file.path].edit = {
            iconClass: 'fa fa-edit',
            text: 'Edit',
            onClick: (file) => this.editFile(file.path),
          }

          obj[file.path].copy = {
            iconClass: 'fa fa-copy',
            text: 'Copy',
            onClick: (file) => this.copyFile = file.path,
          }

          obj[file.path].move = {
            iconClass: 'fa fa-arrows-alt',
            text: 'Move',
            onClick: (file) => this.moveFile = file.path,
          }

          obj[file.path].rename = {
            iconClass: 'fa fa-pen',
            text: 'Rename',
            onClick: (file) => this.fileToRename = file.path,
          }

          obj[file.path].info = {
            iconClass: 'fa fa-info',
            text: 'Info',
            onClick: (file) => this.showInfoFile = file.path,
          }

          obj[file.path].delete = {
            iconClass: 'delete fa fa-trash',
            text: 'Delete',
            onClick: (file) => this.fileToRemove = file.path,
          }
        } else {
          obj[file.path].delete = {
            iconClass: 'delete fa fa-trash',
            text: 'Delete',
            onClick: (file) => this.directoryToRemove = file.path,
          }
        }

        return obj
      }, {})
    },

    fileIcons() {
      return this.files.reduce((obj, file) => {
        if (file.type === 'directory') {
          obj[file.path] = 'fa-folder'
        } else {
          const mime = this.mimeTypes[file.path] || ''
          switch (true) {
            case mime.startsWith('audio/'):
              obj[file.path] = 'fa-file-audio'
              break
            case mime.startsWith('video/'):
              obj[file.path] = 'fa-file-video'
              break
            case mime.startsWith('image/'):
              obj[file.path] = 'fa-file-image'
              break
            case mime.startsWith('text/'):
              obj[file.path] = 'fa-file-alt'
              break
            default:
              obj[file.path] = 'fa-file'
              break
          }
        }

        return obj
      }, {})
    },

    hasHomepage() {
      return Object.keys(this.homepage || {}).length
    },

    pathTokens() {
      if (!this.path)
        return []

      if (!this.path?.length)
        return ['/']

      return ['/', ...this.path.split(/(?<!\\)\//).slice(1)].filter((token) => token.length)
    },

    showCopyModal() {
      return this.copyFile != null || this.moveFile != null
    },
  },

  methods: {
    initOpts() {
      const args = this.getUrlArgs()
      if (args.showHidden != null)
        this.opts.showHidden = !!args.showHidden

      if (args.sortBy != null)
        this.opts.sortBy = args.sortBy

      if (args.reverseSort != null)
        this.opts.reverseSort = !!args.reverseSort

      if (args.file != null)
        this.editedFile = args.file
    },

    async refresh() {
      this.loading = true
      this.$nextTick(() => {
        // Scroll to the end of the path navigator
        if (this.$refs.nav) {
          this.$refs.nav.scrollLeft = 99999
        }

        // Scroll to the top of the items list
        if (this.$refs.items) {
          this.$refs.items.scrollTop = 0
        }
      })

      try {
        this.files = await this.request(
          'file.list',
          {
            path: this.path,
            sort: this.opts.sortBy,
            reverse: this.opts.reverseSort,
          }
        )

        this.$emit('path-change', this.path)
        this.setUrlArgs({path: decodeURIComponent(this.path)})
      } finally {
        this.loading = false
      }

      await this.refreshMimeTypes()
    },

    async refreshMimeTypes() {
      this.mimeTypes = await this.request(
        'file.get_mime_types', {
          files: this.files
                     .filter((file) => file.type !== 'directory')
                     .map((file) => file.path)
        })
    },

    viewFile(path) {
      window.open(`/file?path=${encodeURIComponent(path)}`, '_blank')
    },

    async editNewFile(name) {
      return await this.editFile(`${this.path}/${name}`, {newFile: true})
    },

    async editFile(path, opts) {
      const force = !!opts?.force
      const newFile = this.isNewFileEdit = !!opts?.newFile

      if (force) {
        this.editWarnings = []
      } else {
        if (!newFile) {
          const [info, isBinary] = await Promise.all([
            this.request('file.info', {files: [path]}),
            this.request('file.is_binary', {file: path}),
          ])

          const size = info?.[path]?.size || 0

          if (isBinary) {
            this.editWarnings.push('File is binary')
          }

          if ((info[path]?.size || 0) > 1024 * 1024) {
            this.editWarnings.push(`File is too large (${this.convertSize(size)})`)
          }

          if (this.editWarnings.length) {
            this.editedFile = path
            return
          }
        }
      }

      this.editedFile = path
    },

    async deleteFile() {
      if (!this.fileToRemove)
        return

      this.loading = true
      try {
        await this.request('file.unlink', {file: this.fileToRemove})
      } finally {
        this.loading = false
        this.fileToRemove = null
      }

      this.refresh()
    },

    async deleteDirectory(directory, opts) {
      directory = directory || this.directoryToRemove
      if (!directory)
        return

      const recursive = !!opts?.recursive
      let isNotEmpty = false
      this.loading = true

      try {
        await this.request('file.rmdir', {directory, recursive})
      } catch (error) {
        if (typeof error === 'string' && error.search(/^\[?Errno 39\]?/i) >= 0) {
          isNotEmpty = true
        }
      } finally {
        this.loading = false
        this.directoryNotEmpty = isNotEmpty
        if (!isNotEmpty) {
          this.directoryToRemove = null
        }
      }

      if (isNotEmpty) {
        this.directoryToRemove = directory
      } else {
        this.refresh()
      }
    },

    async createDirectory(name) {
      if (!name)
        return

      this.loading = true
      try {
        await this.request('file.mkdir', {directory: `${this.path}/${name}`})
      } finally {
        this.loading = false
      }

      this.refresh()
    },

    async copyOrMove(target) {
      let operation = null
      let file = null
      if (this.copyFile) {
        operation = 'copy'
        file = this.copyFile
      } else if (this.moveFile) {
        operation = 'move'
        file = this.moveFile
      } else {
        return
      }

      this.loading = true
      try {
        await this.request(`file.${operation}`, {source: file, target})
        this.notify({
          text: `File ${operation} completed successfully`,
          title: 'Success',
          image: {
            icon: 'check',
          },
        })
      } finally {
        this.loading = false
        this.copyFile = null
        this.moveFile = null
      }

      this.refresh()
    },

    async renameFile(newName) {
      if (!this.fileToRename || !newName?.trim()?.length)
        return

      this.loading = true
      try {
        await this.request('file.rename', {file: this.fileToRename, name: `${this.path}/${newName}`})
      } finally {
        this.loading = false
        this.fileToRename = null
      }

      this.refresh()
    },

    clearEditFile() {
      this.editedFile = null
      this.editWarnings = []
    },

    downloadFile(path) {
      window.open(`/file?path=${encodeURIComponent(path)}&download=true`, '_blank')
    },

    onOptsChange(opts) {
      this.opts = opts
    },

    onBack() {
      if (!this.path?.length || this.path === '/')
        this.$emit('back')
      else
        this.path = [...this.pathTokens].slice(0, -1).join('/').slice(1)
    },

    onItemSelect(file) {
      if (file.type === 'directory')
        this.path = file.path
      else
        this.$emit('input', file.path)
    },

    onSelectCurrentDirectory() {
      this.$emit('input', this.path)
    },

    onUploadCompleted() {
      this.refresh()
    },
  },

  watch: {
    initialPath() {
      this.path = this.initialPath
    },

    opts: {
      deep: true,
      handler() {
        this.setUrlArgs(this.opts)
        this.refresh()
      },
    },

    path(val, oldVal) {
      if (oldVal === val)
        return

      this.refresh()
    },

    showUpload(val) {
      const uploader = this.$refs.uploader
      if (val) {
        uploader?.open()
        this.$nextTick(() => {
          uploader?.focus()
        })
      } else {
        uploader?.close()
      }
    },
  },

  mounted() {
    const args = this.getUrlArgs()
    if (args.path)
      this.path = args.path

    this.initOpts()
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

$btn-container-width: 1.5em;

.browser {
  height: 100%;
  display: flex;
  flex-direction: column;

  .item {
    .actions {
      display: inline-flex;
      justify-content: right;
    }
  }

  .items {
    height: calc(100% - #{$nav-height});
    overflow: auto;
  }

  .nav {
    width: 100%;
    display: flex;
    flex-direction: row;
    padding: 0 !important;

    .btn-container {
      width: $btn-container-width;
      display: inline-flex;
      justify-content: center;
      align-items: center;

      button {
        padding: 0;
        background: none;
        border: none;
        cursor: pointer;

        &:hover {
          color: $default-hover-fg;
        }
      }
    }

    .path-container {
      flex-grow: 1;
      display: inline-flex;
      flex-direction: row;
      overflow: auto;
      padding: 0.5em 1em;

      .path {
        display: inline-flex;
        flex-direction: row;
        align-items: center;
        cursor: pointer;
      }

      .separator {
        width: 1em;
        margin-right: 0.5em;
      }
    }
  }

  :deep(.modal) {
    .body {
      display: flex;
      flex-direction: column;
      padding: 0;
    }

    .modal-body {
      min-width: 20em;
      max-width: 100%;
    }

    ul {
      padding: 1em 0 0.5em 2em;

      li {
        margin-bottom: 0.5em;
        list-style: disc;
      }
    }
  }

  .upload-file-container {
    :deep(.modal) {
      .modal-body {
        position: relative;
      }
    }
  }

  .copy-modal-container {
    :deep(.modal) {
      width: 100%;

      .content {
        width: 80%;
        max-width: 40em;
      }

      .body {
        width: 100%;
        height: 100%;
      }

      .modal-body {
        width: 100%;
        height: 100%;
        position: relative;
      }
    }
  }
}
</style>
