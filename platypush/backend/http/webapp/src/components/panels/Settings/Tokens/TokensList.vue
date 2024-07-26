<template>
  <div class="tokens-list-container">
    <ConfirmDialog ref="tokenDeleteConfirm"
                   @input="deleteToken"
                   @close="tokenToDelete = null">
      <p>Are you sure you want to delete this token?</p>

      <b>
        Any application that uses this token will no longer be able to
        authenticate with the Platypush API. This action cannot be undone.
      </b>
    </ConfirmDialog>

    <Loading v-if="loading" />

    <NoItems :with-shadow="false" v-else-if="!tokens?.length">
      <p>No tokens have been generated yet.</p>
    </NoItems>

    <div class="main" v-else>
      <div class="tokens-list">
        <div class="token" v-for="token in tokens" :key="token.id">
          <div class="info">
            <div class="name"><b>{{ token.name }}</b></div>
            <div class="created-at">
              Created at: <b>{{ token.created_at }}</b>
            </div>
            <div class="expires-at">
              Expires at: <b>{{ token.expires_at }}</b>
            </div>
          </div>
          <div class="actions">
            <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
              <DropdownItem text="Delete"
                            icon-class="fa fa-trash"
                            @input="tokenToDelete = token" />
            </Dropdown>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import Loading from "@/components/Loading";
import NoItems from "@/components/elements/NoItems";
import Utils from "@/Utils";

export default {
  name: "Token",
  mixins: [Utils],
  components: {
    ConfirmDialog,
    Dropdown,
    DropdownItem,
    Loading,
    NoItems,
  },

  data() {
    return {
      loading: false,
      tokens_: [],
      tokenToDelete: null,
    }
  },

  computed: {
    tokens() {
      return this.tokens_.map(token => ({
        ...token,
        created_at: token.created_at ? this.formatDateTime(token.created_at, false, false) : 'N/A',
        expires_at: token.expires_at ? this.formatDateTime(token.expires_at, false, false) : 'never',
      }))
    },
  },

  methods: {
    async refresh() {
      this.loading = true
      try {
        this.tokens_ = (await axios.get('/tokens')).data?.tokens
      } catch (e) {
        console.error(e.toString())
        this.notify({
          text: e.response?.data?.message || e.response?.data?.error || e.toString(),
          error: true,
        })
      } finally {
        this.loading = false
      }
    },

    async deleteToken() {
      if (!this.tokenToDelete) {
        return
      }

      this.loading = true
      try {
        await axios.delete(
          '/tokens',
          {
            data: {
              token_id: this.tokenToDelete.id,
            }
          }
        )

        await this.refresh()
      } catch (e) {
        console.error(e.toString())
        this.notify({
          text: e.response?.data?.message || e.response?.data?.error || e.toString(),
          error: true,
        })
      } finally {
        this.loading = false
      }
    },
  },

  watch: {
    $route() {
      this.refresh()
    },

    tokenToDelete(value) {
      if (value) {
        this.$refs.tokenDeleteConfirm.open()
      } else {
        this.$refs.tokenDeleteConfirm.close()
      }
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

<style lang="scss">
@import "style.scss";

.tokens-list-container {
  position: relative;

  .tokens-list {
    width: 30em;
    max-width: calc(100% + 4em);
    margin: -2em;

    .token {
      width: 100%;
      display: flex;
      align-items: center;
      padding: 0.5em 1em;
      box-shadow: $border-shadow-bottom;
      cursor: pointer;

      &:hover {
        background: $hover-bg;
      }

      .info {
        flex: 1;
      }

      .created-at, .expires-at {
        font-size: 0.8em;
        opacity: 0.8;
      }
    }
  }
}
</style>
