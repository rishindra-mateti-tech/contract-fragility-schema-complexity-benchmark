# DigitalOcean Pinned Source Closure Audit Report

**Policy ID:** `PINNED_SOURCE_CLOSURE_ACQUISITION_POLICY_001`  
**Source Candidate:** `CAND-003` (DigitalOcean)  
**Immutable Commit SHA:** `e326f5060794769b6835084e48be7ce4db062d39`  
**Total Closure Files:** `49`  
**Cryptographically Verified Files:** `49`  
**Hash Mismatches:** `0`  
**Missing Files:** `0`  
**Extra Untracked Files:** `0`  

## 1. Operation Offline Reference Closure Status

| Slot ID | Operation ID | Target Specification File | Closure Status | Details |
| :--- | :--- | :--- | :---: | :--- |
| `SLOT_DO_01` | `floating_ips_create` | `resources/floating_ips/floatingIPs_create.yml` | `VERIFIED_OFFLINE` | All transitive references resolved |
| `SLOT_DO_02` | `domains_create` | `resources/domains/domains_create.yml` | `VERIFIED_OFFLINE` | All transitive references resolved |
| `SLOT_DO_03` | `droplets_create` | `resources/droplets/droplets_create.yml` | `VERIFIED_OFFLINE` | All transitive references resolved |

## 2. Acquired Closure Files (49)

| Relative Path | Size (Bytes) | Git Blob SHA | SHA-256 Checksum |
| :--- | :---: | :--- | :--- |
| `resources/domains/domains_create.yml` | 1061 | `342bd3be99ecd14aa92d582dd4d0e2671061f0f7` | `c8563975bca87695c6c46fa01cc2f7df24c3c594378a9a2c4ca34f07b9e8df9c` |
| `resources/domains/examples/curl/domains_create.yml` | 237 | `58b7d30bda015355f7c909ac1729deec780c7793` | `6a4abe0936b5b7617f4e545f4dd1c1f4f5fd880167ab6a9937e07ee181157244` |
| `resources/domains/examples/go/domains_create.yml` | 439 | `bb057b351aa9fd43e8ebbdaf8636cf57b5ac79da` | `489600b77772c792e30684b1ba527515eea001e89aee68142c8d8ff0e5697a97` |
| `resources/domains/examples/python/domains_create.yml` | 208 | `ff31f05a7b3e071fcf38bf0ee4f33af7621b9f7c` | `08c4e1ef03e909803b4e18686a9dab1cd8071db513d2694c92e390ffea31ccd5` |
| `resources/domains/examples/ruby/domains_create.yml` | 260 | `db05b461482cce59bfa1d0ca2013fc35c3ed0108` | `8221e870c88369dd5c4f03ce5a78815db48f795874d9ae4f817d0f35d79237b6` |
| `resources/domains/models/domain.yml` | 1623 | `9226fb73f429ee5adae9bed17584e1d8a392ea46` | `3c4379df9e816d3a290fb52aefbfa0643f81155996163d05671e67a3f01e25f0` |
| `resources/domains/responses/create_domain_response.yml` | 651 | `b69b4338094000de2729dacf70372cdc66b4bb77` | `1318d10405a77a5fb1ac3de50d0bb9f95c13ac16d830088777b1cc37591d3ccb` |
| `resources/droplets/droplets_create.yml` | 2525 | `a8b4aa04640694cd05ade5787cf18a6e478dac1b` | `0d61cd981785e7a282d5b0ea19dde936fb03072e892c112ee44377338f1059ee` |
| `resources/droplets/examples.yml` | 965 | `d19b4e7b8be1aab9c5113e8fcbffa287822854a6` | `69ded01755d7f2229f117870bbf2f00577d96f4f5f8f03d30c045a16be6665d2` |
| `resources/droplets/examples/curl/droplets_create.yml` | 583 | `6fdc7774b3221338cbb93fb8604ec402ee8ac447` | `0c7cf30be51269e449d801bf0ea167b124ce8915c8a8abd6c5b3d5afa503af19` |
| `resources/droplets/examples/go/droplets_create.yml` | 1005 | `09e509c3b71df3d874176ef87093d69a473c4e21` | `bc251a25c35a22016c7edee69deb736d69ccebc723c4c98e2286747470690630` |
| `resources/droplets/examples/python/droplets_create.yml` | 681 | `49dab9029473ea9e1e4e550c95b26500eb010470` | `d164e925d80260409dc41f49c36f58952be7ee74d82f460f3f25992111445893` |
| `resources/droplets/examples/ruby/droplets_create.yml` | 650 | `a844c73c4529fbe60865e5494664bd8a53c8b95c` | `0b61091377aef774f3bdec466c8f97c8c4d68b0a697c692c66e48e32ef80aab2` |
| `resources/droplets/models/droplet.yml` | 4742 | `b310ec87707468c195f4e0c5d05a4028e3ffeb60` | `a26251cbfc855b6e40a42593dc9c0d905f62511ef29e2f922ff0f04ee51d4e1c` |
| `resources/droplets/models/droplet_backup_policy.yml` | 870 | `9078d776b5352d4afae9250609c6d7a2bc94832c` | `69ae4cc04d5505f76c38af65f94c7349f7bdfb972fc6463ed773997c6f422a4f` |
| `resources/droplets/models/droplet_create.yml` | 5124 | `6a786c69c6e49fd119ade14cfeda14ebbc6bbb1b` | `d5f75fcb0185099cddd828e4dffaf7892e643ac78cdee50d839a2e988074e15e` |
| `resources/droplets/models/droplet_multi_create.yml` | 755 | `dadb0c835aaab48fbd711f215dabdff5f06f9cda` | `7b8178df552f27cbcdc42211f3679e7f12eed52cf0cab21444c002431fd09060` |
| `resources/droplets/models/droplet_next_backup_window.yml` | 475 | `dda61ca2896791d460ac4cb5a8f3b28d5e6f562c` | `aad2159781388152ca8a4f966f7759eb1a908d6b36ac08f4df5b33834c3cd625` |
| `resources/droplets/models/droplet_single_create.yml` | 647 | `1fa5b56a1a614a70269cf719b79745fc258d22b1` | `26bfa621ca33dc796fc115bc4822a52aa47d03ba8e80adc2d05d909f6ae38aa0` |
| `resources/droplets/models/kernel.yml` | 988 | `08e6aa58740715f4c669e2d3b9a6059e398538fd` | `5df2d14346e54707fd15358b4a9271ee230e2845ee0e0e6a86edb4ed1b84fcb3` |
| `resources/droplets/models/network_v4.yml` | 683 | `f2ce887184cd51f43314bbbcccf61c4adb7fd7ba` | `eb11ff6402724d07f3afa86ece13bb31796d2451ae14d75ebaa75e60fc21d649` |
| `resources/droplets/models/network_v6.yml` | 636 | `8974fc3e27242a090cc484867456e9fcc4fd5e19` | `ff072a4b319a2c12982b97bcf8a3eadf95b27169df070c9bc8da6ed39f38966e` |
| `resources/droplets/responses/droplet_create.yml` | 1335 | `7adf2b817efe628c9ad19c8b01461adef6e5df19` | `3caa45eca90a7c642c92cd423b9c1fd307002a9722f4d6f9abdeebbe9599d485` |
| `resources/droplets/responses/examples.yml` | 27384 | `2c57336894be2a331f5912bbf7870c1fb841c2e8` | `fdd922f5c8bec2ed2c298fb32e791d5b1813e8e2979ab854570ce4514b8e9f90` |
| `resources/floating_ips/examples/curl/create_floating_ip.yml` | 220 | `799f329e767415daa4af13434aa6fa07f2e4afa1` | `19cbe641d217b0c05bea058ddd32f90451d7051d2b8c821bd936eb6368d2c34e` |
| `resources/floating_ips/examples/go/create_floating_ip.yml` | 331 | `8e2b8c3b4eb7dbe95fb0432746c9d15d86637e9e` | `c2f4bf44699ab57dca426f7750d5f85db295f95ad43187b2a80fa5399833a780` |
| `resources/floating_ips/examples/ruby/create_floating_ip.yml` | 244 | `760ce63b707f23e7bb613657e7d79b47944c7e82` | `0d4316f14ec955d880c6d078ba539d571ee4f5f74062e5a3ea2ce6d98d3c9e48` |
| `resources/floating_ips/floatingIPs_create.yml` | 1133 | `ad2918438c7d060155c254e411d393bff72b4d7b` | `619d2193ca5c0ff67dc9614d984edc637c28a7e716f661fe677783bb7fba3735` |
| `resources/floating_ips/models/floating_ip.yml` | 1394 | `3754c89c1c70b7493c829c85c27986ffda4935de` | `d7f4bccde7ef75aad1d200c7ecee1ebca32521b9d98272a2b84df65a19272659` |
| `resources/floating_ips/models/floating_ip_create.yml` | 645 | `c59b803326d235ec685f40b19ffbbf2555c7e254` | `57292ded9178c1c0f22a902c3bf16167bbd3b0b162887ac05aefd65269200bfc` |
| `resources/floating_ips/responses/examples.yml` | 6287 | `0d090ff4fd3d902a871e8e493e30bf8dcea25a20` | `e5c9ccee7a1f4d2a5fb23408c4ac54760b82b9f568fe320a229cf3b4b251b800` |
| `resources/floating_ips/responses/floating_ip_created.yml` | 1310 | `105bc9f2e958e1e502fd3f27b5ed6f9e209aea3a` | `60968f61ec57a6a407d0bde40b86d753f70a33096f172c3c7d0650ea044aff8d` |
| `resources/images/attributes.yml` | 418 | `c65a988f4b4da777a749499e2bfb6f026e8ed7fd` | `c5f0c5572beae4f9158e4189cfa3ce7e7c3024fa42caaec93ca42a2aafbec569` |
| `resources/images/models/image.yml` | 2676 | `7867ae9af3e92a1258743fda810b34e179a34d64` | `090edab623a90d6efe9c4ed12f1c00ae6f8019b4aa3d29de2c38e3743008de9d` |
| `resources/regions/models/region.yml` | 1426 | `a16baf69456db024ac21146db5fdc67019c8151b` | `ec1e4b4a96715fd6e2325f43d53db7ef6d0ef2b245bfd5d02019faecbb6b03bd` |
| `resources/sizes/models/disk_info.yml` | 569 | `e7edcdd5afcfa11c28ed91f741bce4eec1180fad` | `80b90a1126eef3beabfda8ad6aebe974e7bcf9db1c5b237bf4bcc12a1d9f982f` |
| `resources/sizes/models/gpu_info.yml` | 604 | `ffcd4c6ee3062f7799764328484e34bc145a2fab` | `b878c6ae1cfd8e8dcde3fe4d4bcbf6c3ee5b1c15a8f64e514f9728fbe5adb815` |
| `resources/sizes/models/size.yml` | 2504 | `1f62f31e9578f38028188f81ca5ee451e9e8763d` | `9669809be28c2a09164c09ac26210d593d21389bedd62861a175185f8dd10fe9` |
| `shared/attributes/distribution.yml` | 546 | `946c340f41251a14440d8414ffd31780b4eb9698` | `d13989a2ea849607b2d932a7e0d8e720f22e7428cf51d62b6f31b2e280ded2bc` |
| `shared/attributes/region_slug.yml` | 272 | `721a7d973e982fe64322485f35dea9b195998327` | `60f66750e984862a9b94a6412861b711b435dbc4cb3ffa7687072d16559eca91` |
| `shared/attributes/regions_array.yml` | 226 | `1391dbfb72412d8b754ea34d70515808e59e90a0` | `f1a4f0e5e603b8baf28813dad9124584621418bea3ac0f2fe842c825835c327d` |
| `shared/attributes/tags_array.yml` | 259 | `5c21bb199694778f02c90b3ffbbc245acb271c42` | `0892b63e8c4bba8164977e671465b8de898ffee7438f2404167f09bd7f282872` |
| `shared/headers.yml` | 1646 | `be2aeec189c391b4a897954ff3648a8242f7da11` | `6d7b7509a87da53de6dd8436af6646c8d6f7255e210d5875d8449a273f451f36` |
| `shared/models/action_link.yml` | 534 | `cf69dc55585c92a0cc68ea5e1f32a8b6bdbb5f92` | `cb9bba19e3c18dc680d3ac3fcde97f7e5c4957f3d639190d45c37db413f6b80a` |
| `shared/models/error.yml` | 799 | `9ade7957cffd1b3483f28718445ac420b3807e52` | `dbb6b736e0a146a577572661147b34a898df5e5994635f87a9230d1ab1087b6f` |
| `shared/responses/server_error.yml` | 402 | `064b4fb5cab8c9c828113da017dc0d877ae3c739` | `64c0fa3daae5a2ee702b0771a34afd3898031bc3c0c75b22095129a3a1499488` |
| `shared/responses/too_many_requests.yml` | 415 | `59324487c73350f9e82f4d0db639c045fb6c576a` | `359c4b1eb758e60333be4bad101f3efd5d30323da83c7ca625fc0385a73e15b5` |
| `shared/responses/unauthorized.yml` | 425 | `e6083aeea1fe8075750f6d1eb58e332820e2f4fc` | `7139c8a3a23680afc3a8945eb344c8c91dce6e5c87d0bf0aa5975e38f982914c` |
| `shared/responses/unexpected_error.yml` | 398 | `c922d0eee4f3612e140d730ed71e763ae5ad5e9e` | `3c82e1d9ceb61e9c2493d770969a597de85ba088777a8682fab7b0267eb4c449` |
