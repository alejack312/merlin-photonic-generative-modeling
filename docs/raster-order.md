## Mechanism: why raster order fragments the ring, why radius order doesn't

I pulled the actual bin-level data to make this concrete rather than hand-wavy.

**How raster order is built.** `bin_centers.py` builds the grid with `meshgrid(..., indexing="ij")` then `.ravel()`. That means: fix x, sweep y from low to high (one column), *then* jump to the next x and sweep y again. So walking through raster index = walking down one vertical column of the grid, then teleporting to the next column and walking down again.

**What that does to a ring.** A ring is a curve, not a column. Slice it with a single vertical line (fixed x) and it crosses that line at just two points — the top of the ring and the bottom. Look at actual columns from `p_real`:

```
col 8  (x=0.41): on rows [2, 3, 16, 17]
col 9  (x=0.47): on rows [2, 3, 16, 17]
col 10 (x=0.53): on rows [2, 3, 16, 17]
```

Four little clusters per column — top-left/top-right of the ring and bottom-left/bottom-right — separated by 12+ empty rows in between, *within the same column*. Then raster order jumps to the next column, which has its own on-bins at different rows. Nothing about that jump lines up with the previous column's on-bins, because the ring curves. Every column contributes its own disconnected little cluster(s), and there are ~17 populated columns × ~2-4 clusters each ≈ 44 disjoint fragments. The fragmentation is a direct consequence of "ravel a curved shape column-by-column."

**What radius sorting does.** Radius is a single number computed per bin: distance from `(0.5, 0.5)`. Sorting by it means "put all bins with similar radius next to each other in rank order" — regardless of which column or row they originally came from. A ring is, almost by definition, the set of points at *approximately one radius*. So once you sort by radius, every bin belonging to the inner ring lands in one contiguous block of ranks, and every bin belonging to the outer ring lands in another contiguous block. Checking it directly:

```
rank[112:147]  radius [0.382, 0.421]  width=36 bins   <- inner ring, one solid block
rank[170:215]  radius [0.466, 0.523]  width=46 bins   <- outer ring, one solid block
rank[164:168], [217:218], [222:222], [225:226], [229:230]  -- five tiny 1-2 bin satellites
```

Two rings really did collapse to two big contiguous blocks, exactly as claimed. The honest addendum: it's not *exactly* two — there are five tiny 1-2-bin satellite fragments right at the boundary of the outer block, caused by grid quantization (the finite 21×22 grid can't represent "distance 0.538" and "distance 0.523" as adjacent ranks when other bins fall between them in the sort but happen to be off). That's a minor, expected discretization artifact, not a flaw in the reasoning — worth knowing if you're ever asked "so is it exactly two bands?"

## Plain-language version, first

The circuit doesn't output "x,y points." It outputs a list of 462 numbers — think of them as **462 numbered boxes**, each holding a little bit of probability. To turn that into a 2D picture, we decided ahead of time which (x,y) location each box number belongs to. That decision — "box #7 = this spot on the grid" — is the whole story. Get it right, and a picture the circuit naturally likes to draw becomes a ring. Get it wrong, and the exact same picture becomes confetti.

## The analogy

Imagine a square garden with a circular flower bed running through it — like a donut shape sitting in a square yard. You tile the whole yard into a grid and you want to hand each tile a number, 1 through 462, so you can describe "which tiles have flowers" as a simple list of numbers.

**Method A — read it like a book.** Start at the bottom-left corner, walk straight up that column, number the tiles 1, 2, 3... When you hit the top, jump to the *next column over*, start again from the bottom. This is what the old code did (and it's a completely reasonable way to number a grid — nothing "wrong" with it in general).

Now walk through your numbers and ask "flower or no flower?" In any single column, the circular flower bed only crosses that column in one or two short strips (where the ring passes through), then there's a gap, then the column ends. You jump to the next column — and the flower-bed strip there is at some *totally different* set of numbers, because the ring is round, not aligned to your columns. So your "flower / no flower" list looks like: off, off, ON, off,off,off,off,off,off,off,off, ON, off, off... then column ends, next column starts fresh, same thing happens again in a new place. Forty-some tiny disconnected ON-blips. That's raster order.

**Method B — number by distance from the yard's center.** Nearest tile to the center gets #1, farthest tile gets #462, everything in between sorted by distance. Now ask the same question: which tiles have flowers? Well — a ring is, by definition, "everything at roughly one distance from the center." So *every single flower tile has a number that's close to every other flower tile's number*, because they're all roughly the same distance out. All the ON tiles bunch up into one solid stretch of numbers, with a boring stretch of "too close to center" numbers before it and a boring stretch of "too far, out past the ring" numbers after it. No scattering.

## Mapping that back onto the real thing

- The 462 numbered tiles = the 462 numbered output slots of the circuit.
- "Which tiles have flowers" = `p_real`, the real ring-shaped data.
- Method A = the old raster ordering (fix x, sweep y) — verified this really does shatter the ring into ~44 disconnected blips.
- Method B = radius sorting — verified this really does collapse it down to essentially 2 solid blocks (plus a handful of tiny 1-2-tile leftovers from the grid being finite, not a flaw in the idea, just grid roundoff).

Here's the part that makes this matter for *training*, not just bookkeeping: the quantum circuit, because of its physics, naturally produces outputs that are **smooth from one slot number to the next** — nudging its internal dials shifts probability to *neighboring slot numbers*, not to some random distant slot. That's just what the device does; we didn't choose it.

So whatever numbering scheme we pick, the circuit will always try to draw something smooth *in slot-number order*. Under Method A, "smooth in slot order" has nothing to do with the picture's actual shape, so the circuit's natural smoothness gets scrambled into noise once you map it to (x,y). Under Method B, "smooth in slot order" now means "smooth in distance-from-center" — which is *exactly* the kind of smoothness a ring has. So the circuit's natural tendency to be smooth stops fighting the target shape and starts working with it. That's the whole mechanism. Nothing about the circuit itself changed — only which tile each of its numbers points to.

## Where this explanation still has a hole (the honest part)

Distance-from-center only tells you "how far out" a tile is — it says nothing about "which direction around the ring." Two tiles can have the identical radius while sitting on opposite sides of the yard. Radius-sorting fixes the *radial* smoothness problem but does nothing to control *angular* position — so within one ring, the picture can still come out uneven around the circle, denser in some directions than others.

And there's a second assumption baked in that we never actually verified: I claimed the circuit's outputs are smooth from slot to slot, and I ordered the *circuit's* slots by "which photon-occupation states seem physically similar" (center-of-mass of where the photons sit) as a guess at what "neighboring slot" means to the circuit. That guess is weak — when we measured how well the circuit's actual output lines up with the ring shape rank-for-rank, the correlation was only 0.38. So the picture got much better mainly because we fixed the tile-numbering on the *target* side (radius); we're still not confident we numbered the *circuit's own* output slots (Fock states) in the order that's actually physically smooth for it. That's the most likely reason it's "an improvement, not two clean rings."