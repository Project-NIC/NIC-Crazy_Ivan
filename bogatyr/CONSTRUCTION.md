<div align="center">

# Bogatyr: construction

**Where everything sits on the body:** the rules, every module's electrodes muscle by muscle,
the reference and the bias, the IMUs on the bones, and the glove's.

↑ [Bogatyr](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

**A proposal, not yet tried on a body.** Put together from several studies and anatomy books, named
where a place has one, the others estimates; it is to be gone through with someone who knows the
body, a physiotherapist, before any strip is drawn. Distances are estimates unless a source is
named. What the electrodes and the strips are made of is under
[Rubaška](../rubaska/CONSTRUCTION.md#electrodes).

## The electrodes' rules

- **Two chips on the body and on the head, one on the neck:** a module of the body has two ADS1298,
  16 channels on 32 electrodes and a bias electrode, 33, measuring differentially, each channel P
  against N; the head's module two ADS1299, 16 channels on 32 electrodes, a bias and one reference
  electrode, 34, and the neck's one ADS1299, 8 channels on 16 electrodes, a bias and a reference,
  18, both ways on both: against the reference (MISC1 0x20) an ADS1299 puts SRB1 on every channel's
  negative input, so its eight P measure against the reference and the N are idle, INnN reaching the
  amplifier through a switch that is closed only while SRB1 is off (SBAS499C, figure 18; see
  [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)); 514 electrodes on the modules, and the glove's
  and the sock's sixteen with a bias each, 582 in all. **The body's second eight channels are not
  laid out yet:** every module below has its first eight, and the second eight, the crossed pairs
  through the limb and the trunk the owner wants, are laid out with the physiotherapist (see [Open
  questions](#open-questions)).
- **The eight P cover the area's main muscles,** one site each, evenly: on the head and the neck,
  against the reference, they are eight monopolar channels, and any pair of them is formed in
  software.
- **Each N lies 4–8 cm from its P where the muscle allows,** on the neighbouring muscle or further
  along the same one, along the fibres and across them by turns. Mixed along and across pairs
  held up best when the electrodes shifted (Young et al., IEEE TBME 58, 2011; 59, 2012, the
  forearm only). Crosstalk grows with the distance, ~36 % at 2 cm and ~49 % at 4 cm in one case
  (De Luca et al., J Biomech 45, 2012), and no source gives an upper limit; ~10 cm is not exceeded
  here. **On small muscles and near the heart 2–3 cm:** the hand, the foot, the head, the
  sternocleidomastoid, the left chest; SENIAM's own distance is 20 mm on most muscles' pages and
  5–7.5 mm on the abductor pollicis brevis' (seniam.org).
- **On the limbs' rings no N lands on a P:** the P sit round the limb about as far apart as an N
  would lie, so an along N goes 4 cm below its P (5 cm on the thigh) and an across N half a place
  round and 4 cm above the ring. The across pairs turn diagonal, ~25° off the fibres on the upper
  arm and ~45° on the calf by the girths' estimate, along and across at once.
- **No pair crosses the sternum, and the left chest keeps its pairs short:** pairs across the
  sternum carry much more ECG than one-sided ones, the left side more than the right (Oltmann et
  al., IEEE TBME 72, 2025); the QRS on chest pairs grows with their length along the heart, 1.9 mV
  at 8.7 cm (Nedios et al., J Electrocardiol 47, 2014).
- **Left against right in software,** from one-sided channels, not by long pairs across the body:
  the obliques, the latissimus and the iliocostalis differ between a turn to the left and to the
  right, the rectus abdominis and the multifidus do not (Ng et al., J Orthop Res 19, 2001).
- **Across the spine only diagonally, on the erectors' bulges:** a P on one bulge, its N on the
  other a few centimetres higher or lower, ~5–9 cm, so the chords cross in X and each takes both
  sides.
- **The bias over bone,** as SENIAM puts its reference over bone (C7, the wrist, the ankle), and
  on the head and the neck the reference over bone near the middle of the area, close to all
  eight P; the body's modules carry no reference, the ADS1298 having no SRB1.
  Where an IMU needs the same bone, both stay on it a few centimetres apart (see
  [the IMUs](#the-imus)). One bias electrode drives the body and the others wait as spares (see
  [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)).
- **Nothing pressed onto a nerve that lies on bone under the skin:** the common peroneal nerve
  winds round the neck of the fibula, the ulnar nerve rests on the back of the medial epicondyle
  (Gray's *Anatomy of the Human Body*, 1918); an electrode pressed by its band would press the
  nerve against the bone (an inference).
- **The neck sits loose and keeps off the carotid's division.** The common carotid divides opposite
  the upper border of the thyroid cartilage, where it lies comparatively superficially (Gray's, the
  carotid triangle); pressure on the carotid sinus there can slow the heart to a faint in people
  whose sinus is oversensitive, and a tight collar is a known trigger (StatPearls, carotid sinus
  hypersensitivity). Nothing presses there; the neck's fabric is no tighter than a shirt's collar.
- **Mains does not grow with the pair's length** in the model of Merletti & Cerone (J Electromyogr
  Kinesiol 54, 2020): it follows the contacts' mismatch, and the right-leg drive lowers it 5–10
  times. Short strips still help: a shielded trace adds capacitance (an inference).
- **Nothing where the body is pressed:** the palm, which a grip presses, the sole, stood on, and
  the seat, sat on, stay bare, the electrodes there wandering in the signal. What else was left
  out, and why, is under [WHY](WHY.md).

## The modules

"Along" means along the fibres, "across" across them to the neighbour.

### Head, 1 (the headband's front half; Nataša on the back half)

| | P | N |
|---|---|---|
| 1, 5 | frontalis, over the brow's middle, left and right | along, 3 cm higher on the forehead |
| 2, 6 | frontalis, above the brow's outer third | along, 3 cm higher (4 cm out would land by N3) |
| 3, 7 | temporalis' anterior part, at the temple (Castroflorio et al. 2005) | along, 3 cm up |
| 4, 8 | temporalis above the ear | along, 3 cm towards the back of the head |
| 9–16 | with the physiotherapist, as the body's modules' second eight | |

Reference over the left mastoid, bias over the right, the bone behind the ears, low, behind the
earlobe, with Nataša's buttons above them (see [Nataša](../natasa/CONSTRUCTION.md#on-the-head)). All
four pairs run along: across, they would land on the neighbours' places. The headband's back half
carries no electrodes yet: it lies in the hair, over the occipitalis at the sides and only the galea
between them, and it carries Nataša's board (see [Nataša](../natasa/CONSTRUCTION.md#on-the-head));
the electrodes above the ears sit at its front half's edge, their contact to be tried. The head's
second chip's eight channels are laid out with the physiotherapist, and may reach the back half, the
occipitalis at its sides.

### Neck and upper back, 1

| | P | N |
|---|---|---|
| 1, 5 | sternocleidomastoid, its lower part (the innervation zone lies at or above the middle: Falla et al., Clin Neurophysiol 113, 2002) | along, 2–3 cm lower towards its sternal head |
| 2, 6 | splenius capitis, behind the sternocleidomastoid at C2–C3 (estimate, check) | along, 3 cm up and out towards the mastoid, where it inserts under the sternocleidomastoid (Gray's) |
| 3, 7 | upper trapezius, 50 % from the acromion to C7 (SENIAM) | along, 4 cm towards C7 |
| 4, 8 | the neck's extensors beside the spine at C4, on the bulge | across the spine diagonally to the other bulge at C6, ~5 cm |

Reference on C7's spinous process, bias on T4's; the IMUs on C2, and on T2 between them. The face's
turn, one sternocleidomastoid with the other side's splenius (Gray's), is compared in software.

### Shoulder, 2 (each side)

| | P | N |
|---|---|---|
| 1 | deltoid, anterior part (one finger width below and in front of the acromion, SENIAM; sources differ) | along, 4 cm down |
| 2 | deltoid, middle part, at its greatest bulge on the line from the acromion to the lateral epicondyle (SENIAM) | across, 5 cm back to the posterior part, below N3 |
| 3 | deltoid, posterior part, two finger widths behind the acromion's angle (SENIAM) | along, 4 cm down |
| 4 | pectoralis major, clavicular part, below the clavicle's middle | across, 5 cm out to the anterior deltoid over the groove |
| 5 | trapezius, middle part, at T3 between the scapula and the spine (SENIAM) | along, 4 cm out towards the acromion, near the scapula's spine's root |
| 6 | trapezius, lower part, at 2/3 from the scapula's spine towards T8 (SENIAM) | along, 4 cm up towards the scapula's spine |
| 7 | latissimus dorsi, its upper part beside the scapula's lower angle, out from the erectors, which add crosstalk (Ginn & Halaki, J Electromyogr Kinesiol 25, 2015) | along, 4 cm up towards the armpit |
| 8 | serratus anterior, on the side at the sixth rib | across, 4 cm back to the latissimus; on the left 3 cm, near the heart |

The acromion carries an IMU. On the scapula's spine, from its root outwards, ~3–4 cm apart: N5,
the bias, an IMU. **The left serratus lies where the ECG's chest lead V6 is put,** on the
mid-axillary line at the fifth intercostal space: a long pair there would carry much ECG, so its
N stays short. The deltoid's three pairs lie tight round the acromion; to be laid on a body.

### Chest and abdomen, 1

| | P | N |
|---|---|---|
| 1, 5 | pectoralis major, sternal part, above the breast | along, 4 cm out towards the armpit; on the left 3 cm |
| 2, 6 | rectus abdominis, 3 cm beside the midline at the navel | along, 4 cm up |
| 3, 7 | external oblique, below the ribs at the side, along its fibres (Ng et al., Electromyogr Clin Neurophysiol 38, 1998) | along, 4 cm down and in |
| 4, 8 | internal oblique, below the anterior superior iliac spine, its fibres nearly horizontal (Ng 1998) | along, 5 cm in towards the rectus' outer edge, below the spines' level |

On the sternum, ~5–6 cm apart: the bias on the manubrium, the IMU on the body's middle. **No
pair reaches the xiphoid:** pairs to it had the ECG ~30 dB above the breathing muscles' EMG
(Oltmann 2025). On a woman the pectoralis' places sit above the breast, the serratus beside it.

### Lower back, 1

| | P | N |
|---|---|---|
| 1, 5 | the thoracic erectors at T9, on the bulge (they follow the trunk's turn: McGill, J Orthop Res 9, 1991) | across the spine diagonally to the other bulge at T11, ~7–8 cm |
| 2, 6 | longissimus, two finger widths beside L1 (SENIAM) | across the spine diagonally to the other bulge at L2, ~7 cm |
| 3, 7 | iliocostalis at L2 (SENIAM) | along, 4 cm up its line |
| 4, 8 | multifidus at L5, 2–3 cm from the midline (SENIAM) | across the spine diagonally to the other side at L4, ~5 cm |

L3's spinous process carries an IMU; the multifidus' N lie 2–3 cm beside L4, tight. Bias on the
sacrum's middle crest at S3, the IMU at S1 above it. The lower trapezius and
the upper latissimus are the shoulders'.

### Hip, 2 (each side; nothing where one sits)

| | P | N |
|---|---|---|
| 1 | tensor fasciae latae, in the top sixth of the line from the anterior superior iliac spine to the knee (SENIAM) | along, 4 cm down |
| 2 | gluteus medius, front fibres, between the spine and the trochanter | across, 5 cm forward to the tensor: both turn the thigh in (Gray's) |
| 3 | gluteus medius, 50 % from the iliac crest to the trochanter (SENIAM) | along, 4 cm down towards the trochanter |
| 4 | gluteus medius, just below the iliac crest | along, 4 cm down |
| 5 | gluteus medius, back fibres | across, 5 cm back to the maximus: abduction against extension |
| 6 | gluteus maximus, upper part, outer | along, 4 cm down and out towards the trochanter |
| 7 | gluteus maximus, upper part, inner, beside the sacrum | along, 4 cm down and out |
| 8 | gluteus maximus, at most down to SENIAM's line from the sacrum to the trochanter | across, 5 cm up to the medius' back fibres |

The IMU on the iliac crest's tubercle, clear of P4; bias on the greater trochanter, which is the
hip's alone. The gluteus maximus' lower part is sat on, and so pressed
like the palm.

### Upper arm, 2

An even ring of eight P round the middle, at 50 % of the line from the acromion to the
olecranon, the triceps' spot (SENIAM); round the forearm, evenly placed electrodes did as well
as electrodes on named muscles (Farrell & Weir, IEEE TBME 55, 2008), which is taken to hold here
too, an inference. Under the ring: the biceps' two heads, the brachialis beside it on the outer
side, the triceps' lateral and long heads. The biceps is placed with the elbow bent, as it
slides under the electrodes (Konrad, *The ABC of EMG*, Noraxon 2005, fig. 24). N1, 3, 5, 7 along,
4 cm below; N2, 4, 6, 8 half a place round and 4 cm above. In the elastic gap on the outer side,
over the humerus' lateral supracondylar ridge, from the elbow up: an IMU and the bias, ~3 cm
apart (an estimate, to check).

### Forearm, 2

| | P | N |
|---|---|---|
| 1–5 | an even ring of five round the forearm's upper part, at 40 % from the medial epicondyle to the ulna's styloid, ~10 cm below the elbow, over the wrist's and fingers' flexors, the extensors and the brachioradialis (Farrell & Weir: eight electrodes evenly round at 40 %, the ulna's edge in a gap) | N1, 3, 5 along, 4 cm below; N2, 4 half a place round and 4 cm above |
| 6–8 | with the physiotherapist, as the module's second eight | |

Four to six channels sufficed for the forearm (Farrell & Weir 2008; Young et al. 2012), which is
why five go there and the rest waits for the physiotherapist. The IMU in the gap over the ulna's
edge, 3–4 cm below the olecranon; bias over the ulna's styloid at the wrist. The hand has a chip
of its own, on the glove's board (see [the glove's](#the-gloves)).

### The hand, the glove's ADS1298

| | P | N |
|---|---|---|
| 1 | first dorsal interosseous, between the thumb and the index | along, 2 cm |
| 2 | abductor pollicis brevis, at the thumb's edge (SENIAM) | along, 2 cm |
| 3 | abductor digiti minimi, at the little finger's edge | along, 2 cm |
| 4–8 | with the physiotherapist: the thenar's and the hypothenar's muscles, the back of the hand under the extensors' tendons | |

On the back only the first dorsal interosseous is sure, the other muscles there being thin under
the extensors' tendons, and the palm stays bare, since every grip presses it (see
[WHY](WHY.md#the-places-weighed)); the bias on the glove's board's own electrode, over the carpus.

### Thigh, 2

An even ring of eight P round the middle of the line from the anterior superior iliac spine to
the patella, ~6 cm apart: the rectus femoris (SENIAM 50 %), the vastus lateralis in front and
behind, the biceps femoris and the semitendinosus (SENIAM 50 %), two over the adductors, and the
vastus medialis' upper edge (its spot lies lower, SENIAM 80 %; estimate). N1, 3, 5, 7 along,
5 cm below; N2, 4, 6, 8 half a place round and 4 cm above. **The thigh has no bone near the skin
at its middle:** the bias over the medial femoral epicondyle, far from the ring, the IMUs 4–5 cm
above both epicondyles; the trochanter is left to the hip's bias. To be tried, the weakest
point.

### Calf, 2

| | P | N |
|---|---|---|
| 1–5 | an even ring of five below the knee: tibialis anterior (SENIAM 1/3 from the fibula's head to the medial malleolus), peroneus longus (SENIAM 25 % from the fibula's head), gastrocnemius lateralis and medialis, the soleus' inner edge (estimate) | N1, 3, 5 along, 4 cm below; N2, 4 half a place round and 4 cm above |
| 6–8 | with the physiotherapist, as the module's second eight | |

On the tibia's inner surface, in the elastic gap: the IMU 3–4 cm below the knee, the bias lower,
the IMU 6–8 cm above the ankle. The bias is not over the fibula's head: the common peroneal nerve
winds round the bone just below it (Gray's). The foot has a chip of its own, on the sock's board
(see [the socks](#the-socks)).

### The foot, the sock's ADS1298

| | P | N |
|---|---|---|
| 1 | extensor digitorum brevis, on the instep's outer side (Branthwaite et al., The Foot 2019) | along, 2 cm |
| 2 | the dorsal interossei, in the first space between the metatarsals (Branthwaite 2019; the space an estimate) | along, 2 cm |
| 3 | abductor digiti minimi, the outer edge (Branthwaite 2019) | along, 2 cm |
| 4–8 | with the physiotherapist; the sole stays bare, which is stood on | |

The bias on the inner side of the heel, over the calcaneus, an estimate.

## What it comes to

| part | modules | P + N | bias + reference | IMUs |
|---|---|---|---|---|
| head | 1 | 32, 16 laid out | 2 | 4 |
| neck and upper back | 1 | 16 | 2 | 2 |
| shoulders | 2 | 64, 32 laid out | 2 | 6 |
| chest and abdomen | 1 | 32, 16 laid out | 1 | 1 |
| lower back | 1 | 32, 16 laid out | 1 | 3 |
| hips | 2 | 64, 32 laid out | 2 | 2 |
| upper arms | 2 | 64, 32 laid out | 2 | 8 |
| forearms | 2 | 64, 20 laid out | 2 | 4 |
| hands, the gloves | 2 | 32, 12 laid out | 2 | 40 |
| thighs | 2 | 64, 32 laid out | 2 | 8 |
| calves | 2 | 64, 20 laid out | 2 | 4 |
| feet, the socks | 2 | 32, 12 laid out | 2 | 16 |
| **the suit** | **16 modules, 2 gloves, 2 socks** | **560, 256 laid out** | **22, 582 electrodes in all** | **98** |

**The heart and the breath.** The heart's ECG shows in the EMG, strongest on the torso and
weaker on the limbs. Cleaning the EMG means estimating the ECG and subtracting it, and the ECG
so removed gives the heart rate and its rhythm for free (see
[Baťa](../bata/SIGNALS.md#the-ecg-and-the-breath)). Breathing shows the same way, in the
diaphragm and the lower abdominal muscles.

## The IMUs

Each IMU measures the orientation of its own segment. Sensor fusion keeps it as a quaternion,
which has no singularity, and a joint's rotation is the difference between two neighbouring IMUs,
again a quaternion. A singularity can only appear when a result is turned into three angles at the
output; see [Porjadok](../porjadok/SOFTWARE.md#output).

- **No magnetometer.** Indoors the steel in a building bends the Earth's field, differently from
  place to place, so no calibration takes it out. Gravity shows an IMU's tilt but not its turn about
  the vertical, and the gyro alone drifts in that. Across a joint the turn is pinned anyway: both
  bones share the joint's centre, and an IMU off the joint's axis runs round a circle, so the
  centre's acceleration worked out from the IMU on either side must agree. Every movement corrects
  the drift. Standing still, a gyro reads nothing but its own offset, which is measured and taken
  off; silent EMG confirms the stillness, since a slow movement that the accelerometers barely see
  still shows in the muscles. Seel, Schauer and Raisch find a joint's axis and centre from such
  constraints (IEEE CCA 2012); Weygers et al. remove the drift using only what the IMUs on two
  connected segments measure in common, and put knee angles 2–4° RMS over 7 minutes of walking (IEEE
  Sensors Journal, 2020; both from the abstracts). What stays unseen is which way the whole body
  faces in the room, and joint angles do not need it.
- **Twist shows as a gradient along the segment.** Turning the palm over is the radius rolling
  round the ulna: the forearm IMU by the wrist turns through almost the whole range, the one by
  the elbow a little, the one on the shoulder hardly at all.
- **The suit never sits the same way twice,** for the IMUs as for the electrodes. A calibration
  pose at the start, a few seconds standing with the arms down or out to the sides, gives the
  model its starting point. IMU motion-capture suits do the same.

**The rules:**

- **Four IMUs a module at most:** two I3C buses of two, since the ICM-45686 has one address pin
  (DS-000489, 9.3); 64 places on 16 modules, 42 fitted. The gloves come on top, 20 each, and the
  socks, 8.
- **At least the segments of a commercial suit:** Xsens MVN puts 17 sensors on the pelvis (the
  sacrum), the sternum, the head, both shoulders (the scapula), the upper arms, the forearms,
  the hands, the thighs, the shanks and the feet (the walking study in PMC3651313); this suit has
  every one of them.
- **Two on each long bone, one near each end:** with no magnetometer every joint is pinned by an
  IMU close on each side of it, and the forearm's twist shows as the difference between its two
  ends.
- **More where the skin slides most:** several IMUs on a bone and the EMG of the muscles that turn
  it let the model tell the skin from the bone. The skin moves most on the thigh, more than
  30 mm, and up to 15 mm on the tibia (Peters et al., Gait & Posture 2010, a systematic review);
  on the upper arm skin markers missed 20–48 % of the bone's turn about its axis (Cutti et al.,
  Gait & Posture 21, 2005), and less with only the markers near the elbow (Warner & Heller, J
  Biomech 2025). So the thigh and the upper arm get four each, three of the upper arm's near the
  elbow, where its epicondyles lie under the skin; the scapula, which slides under the skin, gets
  a second.
- **Over bone and flat places, where the skin slides least;** where an IMU and an electrode need
  the same bone, both stay on it a few centimetres apart.
- **The hand and the foot are the glove's and the sock's:** one board in the limb's fourth slot
  with one ADS1298 and the IMUs, the glove's 20 places, a sock's eight to start (see
  [Rubaška](../rubaska/HARDWARE.md#the-glove)); the forearm's and the calf's modules keep their
  two.

| module | IMUs | places |
|---|---|---|
| head (headband) | 4 | a square on the skull, one rigid bone: the forehead's two over the frontal bone, left and right of Míša's housing above the frontalis' pairs, the middle being his, with his own IMU; the back half's two above the ears' level beside Nataša's board, left and right. Four on one bone are redundancy: their mean halves the noise, and a band that slips shows as the four disagreeing |
| neck and upper back | 2 | C2's spinous process, the first felt below the skull, above the electrodes at C4; T2, between the shoulder blades' tops, between the reference on C7 and the bias on T4 |
| shoulder, each | 3 | the acromion's flat top: the scapula followed from it, with an error under 10°, between 30° and 120° of the arm's elevation (Karduna et al., J Biomech Eng 2001; the figures from a later review, PMC4019455); the scapula's spine, its outer part, beside the bias; the clavicle's middle, near the skin |
| chest and abdomen | 1 | the sternum's body, its middle, below the bias on the manubrium |
| lower back | 3 | the thoracolumbar junction, T12–L1; L3's spinous process, for the lumbar curve; the sacrum's top, S1, the pelvis' sensor (the bias at S3) |
| hip, each | 1 | the iliac crest's tubercle, in front on its outer lip, a second look at the pelvis' tilt |
| upper arm, each | 4 | the outer side at the deltoid's insertion, in the ring's elastic gap; the lowest on the lateral supracondylar ridge, just above the lateral epicondyle (the bias above it); above the medial epicondyle, in front of the ulnar nerve's groove; the back above the olecranon |
| forearm, each | 2 | the ulna's border 3–4 cm below the olecranon; the radius' back ~2 cm above the wrist, on the radius alone, which turns with the hand while the ulna does not; the hand's are the glove's (below) |
| thigh, each | 4 | 5 cm below the greater trochanter's tip on the outer side (the trochanter left to the hip's bias); 4–5 cm above the lateral and the medial epicondyle (the bias on the medial one); the front above the patella (estimate) |
| calf, each | 2 | the tibia's inner surface 3–4 cm below the knee and 6–8 cm above the ankle (the bias between them); the foot's are the sock's (below) |

| | IMUs |
|---|---|
| the body's modules | 42 of 64 places |
| the gloves | 2 × 20 |
| the socks | 2 × 8 |
| all, with two gloves and two socks | 98 |

### The glove's

The glove's board on the back of the hand carries the hand's ADS1298 and 20 IMU places (see
[Rubaška](../rubaska/HARDWARE.md#the-glove)). **The electrodes,** eight channels, three laid out
above and five with the physiotherapist. **The IMUs,** 20 places: on each finger its three
phalanges, the proximal and the middle on the Bratiška's first bus, the distal on the second with
a place to spare; on Staršaja's own buses the thumb's metacarpal and its two phalanges, and the
board's own, on the back of the hand over the carpus; the four spares for the palm's arch, the
fourth and fifth metacarpals' heads, where the arch bends, and a second on the thumb's metacarpal,
because its skin slides. Over bone, not between the bones, where the interosseous muscles bulge
under the skin; the strips along the sides of the fingers. Which are fitted the recordings decide:
20; 12, the thumb's three, the board's own and two a finger, the proximal and the distal; or 8,
the thumb's three, the board's own and one a finger, the proximal, a mitt open at the fingers for
a hand without a glove. The palm's arch bending only past the middle finger is anatomy, not
measured here.

### The socks

Nosok's board sits on the calf above the ankle (see [Rubaška](../rubaska/HARDWARE.md#the-sock));
on the foot its ADS1298's sixteen electrodes, three channels laid out above and five with the
physiotherapist, and up to eight IMUs, the segments of a multi-segment foot model, the Oxford
Foot Model's hindfoot, forefoot and hallux (Stebbins et al., Gait & Posture 23, 2006): the heel
over the calcaneus, the midfoot's inner side, the fourth metatarsal and the hallux's proximal
phalanx, four to start, on Staršaja's own places, the other four, on one Bratiška, for trials,
the forefoot's outer side and the lesser toes among them; over bone, not on the sole, which is
stood on, and clear of the extensor digitorum brevis' and the interossei's pairs. To be laid out
with the hand; the first layout a proposal.

## Open questions

- an hour with a physiotherapist over every place above, before a strip is drawn;
- **the body's modules' second eight channels,** 16 on a limb's module, on the trunk's and on the
  head's, the crossed pairs through the limb and the trunk the owner wants, laid out with the
  physiotherapist before any strip is drawn; the thumb's channels with them;
- **the hand's and the foot's eight channels,** three of each laid out here, the rest with the
  physiotherapist; **the sock's places on the foot,** the heel, the midfoot, the forefoot and the
  hallux on Staršaja's own places and a Bratiška, with the hand's layout;
- the left serratus' pair and its ECG;
- the splenius' and the soleus' places, the latissimus' upper place, marked as estimates;
- the tight places: the deltoid's pairs round the acromion; the scapula's spine with N5, the
  bias, the reference and an IMU; L4's reference beside the multifidus' N; the thumb's metacarpal
  IMU beside the first dorsal interosseous' and the abductor pollicis brevis' electrodes; the
  glove's board over the hand's strip; the headband's: the forehead's IMUs beside Míša's housing
  and the frontalis' pairs, the mastoids under Nataša's buttons;
- whether an N should sit further than 8 cm anywhere: no source gives a limit;
- the hand, asked before any glove is made, since each version of it is a flexible circuit made
  and thrown away: its electrodes' strip under the board and the finger strips on one inner
  layer; and how many of the glove's eight channels the thumb wants. Today it has the abductor
  pollicis brevis at its edge and the first dorsal interosseous on the back; the opponens lies
  beneath the abductor along the first metacarpal, the short flexor and the adductor in the palm,
  and the long flexor in the forearm (Gray 1918, pp. 461–462);
- 24 IMU places left free on the modules, for trials; the heel is the sock's;
- the crossing on the spine and the rings' diagonals against straight pairs, on one arm, and the
  differential way against the reference on the head and the neck: how much the model loses after
  the suit comes off and goes on again.

## Sources

SENIAM's sensor locations (seniam.org); Konrad, *The ABC of EMG*, v1.4 (Noraxon 2005); Falla et
al., Clin Neurophysiol 2002; Ng, Kippers & Richardson, Electromyogr Clin Neurophysiol 1998; Ng et
al., J Orthop Res 2001; McGill, J Orthop Res 1991; McGill, Juker & Kropf, J Biomech 1996; Waite
et al., J Electromyogr Kinesiol 2010; Ginn & Halaki, J Electromyogr Kinesiol 2015; Branthwaite
et al., The Foot 2019; Farrell & Weir, IEEE TBME 2008 (PMC3153447); Young, Hargrove & Kuiken,
IEEE TBME 2011 and 2012; De Luca et al., J Biomech 2012; Merletti & Cerone, J Electromyogr
Kinesiol 2020; Nedios et al., J Electrocardiol 2014; Oltmann et al., IEEE TBME 2025; Castroflorio
et al. 2005; Gray's *Anatomy of the Human Body*, 20th edition (1918): the splenius capitis, the
ulnar nerve, the common peroneal nerve, the carotid triangle; StatPearls, carotid sinus
hypersensitivity; TI's ADS1299 datasheet, SBAS499C. For the IMUs: Xsens MVN's 17 segments in
PMC3651313; Peters et al., *Quantification of soft tissue artifact in lower limb human motion
analysis: a systematic review*, Gait & Posture 2010; Stagni et al., Clin Biomech 2005 (thigh up to
31 mm, shank up to 21 mm); Cutti et al., *Soft tissue artefact assessment in humeral axial
rotation*, Gait & Posture 21, 2005; Warner & Heller, J Biomech 2025; Karduna et al., *Dynamic
measurements of three-dimensional scapular kinematics: a validation study*, J Biomech Eng 2001,
with the review PMC4019455; Stebbins et al., *Repeatability of a model for measuring multi-segment
foot kinematics in children*, Gait & Posture 23, 2006, the Oxford Foot Model; ICM-45686 DS-000489
Rev 1.1.
