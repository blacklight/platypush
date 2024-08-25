<script>

// From https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript
String.prototype.hashCode = function(seed = 0) {
  let h1 = 0xdeadbeef ^ seed, h2 = 0x41c6ce57 ^ seed;
  for(let i = 0, ch; i < this.length; i++) {
    ch = this.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }

  h1  = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
  h1 ^= Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2  = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
  h2 ^= Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return 4294967296 * (2097151 & h2) + (h1 >>> 0);
};

export default {
  name: "Text",
  methods: {
    capitalize(text) {
      if (!text?.length)
        return text

      return text.charAt(0).toUpperCase() + text.slice(1)
    },

    prettify(text) {
      return text.split('_').map((t) => this.capitalize(t)).join(' ')
    },

    indent(text, spaces = 2) {
      return text.split('\n').map((t) => `${' '.repeat(spaces)}${t}`).join('\n')
    },

    formatNumber(number) {
      return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")
    },
  },
}
</script>
