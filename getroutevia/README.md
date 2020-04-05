# Getroutevia plugin for c-lightning

This plugin allows to generate a route with additional constraints.

# Usage

```
$ lightning-cli getroutevia id=026c64f5a7f24c6f7f0e1d6ec877f23b2f672fb48967c2545f227d70636395eaf3 msatoshi=1000 riskfactor=1 include_node=038863cf8ab91046230f561cd5b386cbff8309fa02e3f0c3ed161a3aeb64a643b9
[
   {
      "id": "030f0bf260acdbd3edcad84d7588ec7c5df4711e87e6a23016f989b8d3a4147230",
      "channel": "1666537x383x0",
      "direction": 0,
      "msatoshi": 2491,
      "amount_msat": "2491msat",
      "delay": 193,
      "style": "tlv"
   },
   {
      "id": "038863cf8ab91046230f561cd5b386cbff8309fa02e3f0c3ed161a3aeb64a643b9",
      "channel": "1451219x150x0",
      "direction": 0,
      "msatoshi": 2000,
      "amount_msat": "2000msat",
      "delay": 49,
      "style": "tlv"
   },
   {
      "id": "026c64f5a7f24c6f7f0e1d6ec877f23b2f672fb48967c2545f227d70636395eaf3",
      "channel": "1664668x188x0",
      "direction": 1,
      "msatoshi": 1000,
      "amount_msat": "1000msat",
      "delay": 9,
      "style": "tlv"
   }
]

```

# Searching for a route that includes a given node

One possible constraint is to ensure that the route goes through a particular node.
This is achieved by calling `getroute` in a BFS-like fashion:

1. Call `getroute`. If the route is OK, return it. Otherwise, add channels of route to the list of channels to exclude on the next step.
1. Call `getroute` with each channel from the initial route excluded. If one of the results is OK, return it, otherwise add new routes' channels to the list of excluded channels (in addition to the ones already there).
1. Repeat until an OK route is found or `max_attempts` exceeded.

For example, if the initial route consists of channels `[c1, c2, c3]`, int the next iterations `getroute` is called with `exclude=[c1]`, `exclude=[c2]`, `exclude=[c3]`. Then, if the result of `getroute` with `exclude=[c1]` is `[c11, c12, c13]`, the next iteration calls `getroute` with `exclude=[c1, c11]`, `exclude=[c1, c12]`, `exclude=[c1, c13]`.

# Other constraints

Other constraints are possible, such as a (rather silly) condition that ensures that the last hex digits of all node IDs in the route are not `2`, `4`, or `4` (see the code).