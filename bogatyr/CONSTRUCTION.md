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

- **Both ways on one suit:** every module has 16 electrodes, a bias electrode and a reference
  electrode, 18 a module and 288 on 16 modules. In the differential way (MISC1 0x00) each channel
  is P against N; against the reference (MISC1 0x20) the ADS1299 puts SRB1 on every channel's
  negative input, so the eight P measure against the reference and the N are idle: INnN reaches
  the amplifier through a switch that is closed only while SRB1 is off (SBAS499C, figure 18; see
  [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)).
- **The eight P cover the area's main muscles,** one site each, evenly: against the reference they
  are eight monopolar channels, and any pair of them is formed in software.
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
- **The reference over bone near the middle of the area,** so that it is close to all eight P;
  the bias over bone too, as SENIAM puts its reference over bone (C7, the wrist, the ankle).
  Where an IMU needs the same bone, both stay on it a few centimetres apart (see
  [the IMUs](#the-imus)). One bias electrode drives the body and the others wait as spares (see
  [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)).
- **Nothing pressed onto a nerve that lies on bone under the skin:** the common peroneal nerve
  winds round the neck of the fibula, the ulnar nerve rests on the back of the medial epicondyle
  (Gray's *Anatomy of the Human Body*, 1918); an electrode with its spring would press the nerve
  against the bone (an inference).
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

Reference over the left mastoid, bias over the right, the bone behind the ears, low, behind the
earlobe, with Nataša's buttons above them (see
[Nataša](../natasa/CONSTRUCTION.md#on-the-head)). All four pairs
run along: across, they would land on the neighbours' places. The headband's back half carries
no electrodes: it lies in the hair, over the occipitalis at the sides and only the galea between
them, and it carries Nataša's board (see [Nataša](../natasa/CONSTRUCTION.md#on-the-head)); the
electrodes above the ears sit at its front half's edge, their contact to be tried.

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
the bias, the reference, an IMU. **The left serratus lies where the ECG's chest lead V6 is put,**
on the mid-axillary line at the fifth intercostal space: against the reference the left
shoulder's channel 8 will carry much ECG. The deltoid's three pairs lie tight round the acromion;
to be laid on a body.

### Chest and abdomen, 1

| | P | N |
|---|---|---|
| 1, 5 | pectoralis major, sternal part, above the breast | along, 4 cm out towards the armpit; on the left 3 cm |
| 2, 6 | rectus abdominis, 3 cm beside the midline at the navel | along, 4 cm up |
| 3, 7 | external oblique, below the ribs at the side, along its fibres (Ng et al., Electromyogr Clin Neurophysiol 38, 1998) | along, 4 cm down and in |
| 4, 8 | internal oblique, below the anterior superior iliac spine, its fibres nearly horizontal (Ng 1998) | along, 5 cm in towards the rectus' outer edge, below the spines' level |

On the sternum, ~5–6 cm apart: the bias on the manubrium, the IMU on the body's middle, the
reference low on the body, above the xiphoid. **Against the reference the chest will carry much
ECG:** pairs to the xiphoid had the ECG ~30 dB above the breathing muscles' EMG (Oltmann 2025);
this module is meant for the differential way. On a woman the pectoralis' places sit above the
breast, the serratus beside it.

### Lower back, 1

| | P | N |
|---|---|---|
| 1, 5 | the thoracic erectors at T9, on the bulge (they follow the trunk's turn: McGill, J Orthop Res 9, 1991) | across the spine diagonally to the other bulge at T11, ~7–8 cm |
| 2, 6 | longissimus, two finger widths beside L1 (SENIAM) | across the spine diagonally to the other bulge at L2, ~7 cm |
| 3, 7 | iliocostalis at L2 (SENIAM) | along, 4 cm up its line |
| 4, 8 | multifidus at L5, 2–3 cm from the midline (SENIAM) | across the spine diagonally to the other side at L4, ~5 cm |

Reference on L4's spinous process, L3's carrying an IMU; the multifidus' N lie 2–3 cm beside it,
tight. Bias on the sacrum's middle crest at S3, the IMU at S1 above it. The lower trapezius and
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

Reference on the iliac crest behind the IMU on its tubercle, clear of P4; bias on the greater
trochanter, which is the hip's alone. The gluteus maximus' lower part is sat on, and so pressed
like the palm.

### Upper arm, 2

An even ring of eight P round the middle, at 50 % of the line from the acromion to the
olecranon, the triceps' spot (SENIAM); round the forearm, evenly placed electrodes did as well
as electrodes on named muscles (Farrell & Weir, IEEE TBME 55, 2008), which is taken to hold here
too, an inference. Under the ring: the biceps' two heads, the brachialis beside it on the outer
side, the triceps' lateral and long heads. The biceps is placed with the elbow bent, as it
slides under the electrodes (Konrad, *The ABC of EMG*, Noraxon 2005, fig. 24). N1, 3, 5, 7 along,
4 cm below; N2, 4, 6, 8 half a place round and 4 cm above. In the elastic gap on the outer side,
over the humerus' lateral supracondylar ridge, from the elbow up: an IMU, the reference, the
bias, ~3 cm apart (an estimate, to check).

### Forearm and hand, 2

| | P | N |
|---|---|---|
| 1–5 | an even ring of five round the forearm's upper part, at 40 % from the medial epicondyle to the ulna's styloid, ~10 cm below the elbow, over the wrist's and fingers' flexors, the extensors and the brachioradialis (Farrell & Weir: eight electrodes evenly round at 40 %, the ulna's edge in a gap) | N1, 3, 5 along, 4 cm below; N2, 4 half a place round and 4 cm above |
| 6 | first dorsal interosseous, between the thumb and the index | along, 2 cm |
| 7 | abductor pollicis brevis, at the thumb's edge (SENIAM) | along, 2 cm |
| 8 | abductor digiti minimi, at the little finger's edge | along, 2 cm |

Four to six channels sufficed for the forearm (Farrell & Weir 2008; Young et al. 2012), which
is why five go there and three to the hand. Reference in the gap over the ulna's edge at the
ring's level, the IMU 3–4 cm below the olecranon above it; bias over the ulna's styloid at the
wrist. The hand has no module of its own; on its back only the first dorsal interosseous is taken,
the other three being thin under the extensors' tendons, and the palm stays bare.

### Thigh, 2

An even ring of eight P round the middle of the line from the anterior superior iliac spine to
the patella, ~6 cm apart: the rectus femoris (SENIAM 50 %), the vastus lateralis in front and
behind, the biceps femoris and the semitendinosus (SENIAM 50 %), two over the adductors, and the
vastus medialis' upper edge (its spot lies lower, SENIAM 80 %; estimate). N1, 3, 5, 7 along,
5 cm below; N2, 4, 6, 8 half a place round and 4 cm above. **The thigh has no bone near the skin
at its middle:** the reference over the lateral femoral epicondyle and the bias over the medial
one, both far from the ring, the IMUs 4–5 cm above them; the trochanter is left to the hip's
bias. To be tried, the weakest point.

### Calf and foot, 2

| | P | N |
|---|---|---|
| 1–5 | an even ring of five below the knee: tibialis anterior (SENIAM 1/3 from the fibula's head to the medial malleolus), peroneus longus (SENIAM 25 % from the fibula's head), gastrocnemius lateralis and medialis, the soleus' inner edge (estimate) | N1, 3, 5 along, 4 cm below; N2, 4 half a place round and 4 cm above |
| 6 | extensor digitorum brevis, on the instep's outer side (Branthwaite et al., The Foot 2019) | along, 2 cm |
| 7 | the dorsal interossei, in the first space between the metatarsals (Branthwaite 2019; the space an estimate) | along, 2 cm |
| 8 | abductor digiti minimi, the outer edge (Branthwaite 2019) | along, 2 cm |

On the tibia's inner surface, in the elastic gap: the IMU 3–4 cm below the knee, the reference
at the ring's level, the bias lower, the IMU 6–8 cm above the ankle. The bias is not over the
fibula's head: the common peroneal nerve winds round the bone just below it (Gray's). On the
foot the IMUs take the instep's inner side and the fourth metatarsal; the sole stays bare.

## What it comes to

| part | modules | P + N | bias + reference | IMUs |
|---|---|---|---|---|
| head | 1 | 16 | 2 | 2 |
| neck and upper back | 1 | 16 | 2 | 2 |
| shoulders | 2 | 32 | 4 | 6 |
| chest and abdomen | 1 | 16 | 2 | 1 |
| lower back | 1 | 16 | 2 | 3 |
| hips | 2 | 32 | 4 | 2 |
| upper arms | 2 | 32 | 4 | 8 |
| forearms and hands | 2 | 32 | 4 | 4 + 4 |
| thighs | 2 | 32 | 4 | 8 |
| calves and feet | 2 | 32 | 4 | 4 + 4 |
| **the suit** | **16** | **256** | **32, 288 electrodes in all** | **48** |

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

- **Four IMUs a module at most:** two I3C buses of two, since the ICM-42688-P has one address pin
  (DS-000347, 9.3); 64 places on 16 modules. The gloves come on top, 20 each.
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
- **The hand and the foot from their module, with no extension:** the forearm's and the calf's
  modules carry two IMUs of their own and two beyond the joint, on their bus's own strip, which
  crosses the wrist and the ankle beside the electrodes' (see
  [Rubaška](../rubaska/HARDWARE.md#sensing-module)); with the glove, the hand's IMUs are the
  glove's.

| module | IMUs | places |
|---|---|---|
| head (headband) | 2 | the forehead, over the frontal bone, above the left frontalis' pairs beside Míša's housing, the middle being his, with his own IMU; above the ear on the other side, so that a band that slips is seen |
| neck and upper back | 2 | C2's spinous process, the first felt below the skull, above the electrodes at C4; T2, between the shoulder blades' tops, between the reference on C7 and the bias on T4 |
| shoulder, each | 3 | the acromion's flat top: the scapula followed from it, with an error under 10°, between 30° and 120° of the arm's elevation (Karduna et al., J Biomech Eng 2001; the figures from a later review, PMC4019455); the scapula's spine, its outer part, beside the reference; the clavicle's middle, near the skin |
| chest and abdomen | 1 | the sternum's body, its middle, between the bias on the manubrium and the reference above the xiphoid |
| lower back | 3 | the thoracolumbar junction, T12–L1; L3's spinous process, for the lumbar curve (the reference on L4); the sacrum's top, S1, the pelvis' sensor (the bias at S3) |
| hip, each | 1 | the iliac crest's tubercle, in front on its outer lip, a second look at the pelvis' tilt (the reference on the crest behind it) |
| upper arm, each | 4 | the outer side at the deltoid's insertion, in the ring's elastic gap; the lowest on the lateral supracondylar ridge, just above the lateral epicondyle (the reference and the bias above it); above the medial epicondyle, in front of the ulnar nerve's groove; the back above the olecranon |
| forearm and hand, each | 2 + 2 | the ulna's border 3–4 cm below the olecranon; the radius' back ~2 cm above the wrist, on the radius alone, which turns with the hand while the ulna does not; beyond the wrist the back of the hand over the third metacarpal and the thumb's metacarpal, only when no glove is worn |
| thigh, each | 4 | 5 cm below the greater trochanter's tip on the outer side (the trochanter left to the hip's bias); 4–5 cm above the lateral and the medial epicondyle (the reference and the bias on them); the front above the patella (estimate) |
| calf and foot, each | 2 + 2 | the tibia's inner surface 3–4 cm below the knee and 6–8 cm above the ankle (the reference and the bias between them); beyond the ankle the instep's inner side over the midfoot (the extensor digitorum brevis on its outer side) and the fourth metatarsal (the interossei's pair in the first space) |

| | with no gloves | with the gloves |
|---|---|---|
| the body's IMUs | 48 of 64 places | 44 (the hands' four go to the gloves) |
| the gloves | — | 2 × 20 |
| all | 48 | 84 |

### The glove's

Five Bratiški, one a finger, four IMUs each, 20 in all (see
[Rubaška](../rubaska/HARDWARE.md#the-glove)): on each finger its three phalanges and its
metacarpal, the index's and the middle finger's on the back of the hand, which hardly move against
the wrist, the ring finger's and the little finger's mid-bone, where the palm's arch bends; on the
thumb its two phalanges, its metacarpal and a second on it, because its skin slides. Over bone,
not between the bones, where the interosseous muscles bulge under the skin; the wiring along the
sides of the fingers. The palm's arch bending only past the middle finger is anatomy, not measured
here.

## Open questions

- an hour with a physiotherapist over every place above, before a strip is drawn;
- the reference on the thigh, far from its ring;
- the chest and the left serratus against the reference, with their ECG;
- the splenius' and the soleus' places, the latissimus' upper place, marked as estimates;
- the tight places: the deltoid's pairs round the acromion; the scapula's spine with N5, the
  bias, the reference and an IMU; L4's reference beside the multifidus' N; the thumb's metacarpal
  IMU beside the first dorsal interosseous' and the abductor pollicis brevis' electrodes; the
  glove laid over the hand's electrodes; the headband's: the forehead's IMU beside Míša's housing
  and the frontalis' pairs, the mastoids under Nataša's buttons;
- whether an N should sit further than 8 cm anywhere: no source gives a limit;
- the model takes 64 IMU steps (see [Baťa](../bata/SIGNALS.md)): 48 on the body fit, 44 + 40 with
  the gloves do not;
- 16 IMU places left free, for trials; the heel: with two on the foot it rides with the instep,
  and a third would need a place on the calf's module, which is full;
- the crossing on the spine and the rings' diagonals against straight pairs, and the
  differential way against the reference, on one arm: how much the model loses after the suit
  comes off and goes on again.

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
with the review PMC4019455; ICM-42688-P DS-000347.
