<template>
  <div class="entity network-interface-container" :class="{expanded: !isCollapsed}">
    <div class="head" @click.stop="isCollapsed = !isCollapsed">
      <div class="col-1 icon">
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-10 label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-1 collapse-toggler">
        <i class="fas"
          :class="{'fa-chevron-down': isCollapsed, 'fa-chevron-up': !isCollapsed}" />
      </div>
    </div>

    <div class="body children attributes fade-in" v-if="!isCollapsed">
      <div class="child" v-if="value.bytes_sent">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Bytes sent</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.bytes_sent)" />
        </div>
      </div>

      <div class="child" v-if="value.bytes_recv">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Bytes received</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.bytes_recv)" />
        </div>
      </div>

      <div class="child" v-if="value.packets_sent">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Packets sent</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.packets_sent" />
        </div>
      </div>

      <div class="child" v-if="value.packets_recv">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Packets received</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.packets_recv" />
        </div>
      </div>

      <div class="child" v-if="value.errors_in">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Inbound errors</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.errors_in" />
        </div>
      </div>

      <div class="child" v-if="value.errors_out">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Outbound errors</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.errors_out" />
        </div>
      </div>

      <div class="child" v-if="value.drop_in">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Dropped inbound packets</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.drop_in" />
        </div>
      </div>

      <div class="child" v-if="value.drop_out">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Dropped outbound packets</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.drop_out" />
        </div>
      </div>

    <div class="child head" :class="{expanded: !areAddressesCollapsed}"
      @click.stop="areAddressesCollapsed = !areAddressesCollapsed">
      <div class="col-11 label">Addresses</div>
      <div class="col-1 collapse-toggler pull-right">
        <i class="fas"
          :class="{'fa-chevron-down': areAddressesCollapsed, 'fa-chevron-up': !areAddressesCollapsed}" />
        </div>
      </div>

      <div class="body children attributes fade-in addresses"
          v-if="value.addresses?.length && !areAddressesCollapsed">
        <div class="address-container"
          v-for="address in (value.addresses || [])"
          :key="address.address"
        >
          <div class="child head" :class="{expanded: displayedAddresses[address.address]}"
            @click.stop="displayedAddresses[address.address] = !displayedAddresses[address.address]"
          >
            <div class="col-11 label" v-text="address.address" />
            <div class="col-1 collapse-toggler pull-right">
              <i class="fas"
                :class="{
                  'fa-chevron-down': !displayedAddresses[address.address],
                  'fa-chevron-up': displayedAddresses[address.address]
                }"
              />
            </div>
          </div>
          <div class="body children attributes fade-in address-details"
              v-if="displayedAddresses[address.address]">
            <div class="child" v-if="address.family">
              <div class="label">Family</div>
              <div class="value" v-text="address.family" />
            </div>
            <div class="child" v-if="address.netmask">
              <div class="label">Netmask</div>
              <div class="value" v-text="address.netmask" />
            </div>
            <div class="child" v-if="address.broadcast">
              <div class="label">Broadcast</div>
              <div class="value" v-text="address.broadcast" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'NetworkInterface',
  components: {EntityIcon},
  mixins: [EntityMixin],

  data() {
    return {
      isCollapsed: true,
      areAddressesCollapsed: true,
      displayedAddresses: {},
    }
  },
}
</script>

<style lang="scss" scoped>
@import "common";
</style>
