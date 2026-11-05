<div align="center">

# Bogatyr: construction

**Where everything goes on the body:** the rules, the modules and their counts, the IMUs on the
bones, and the glove's.

↑ [Bogatyr](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

**The electrodes' places are not laid out yet:** we do not know how to lay them out well, and we
are asking professionals for advice (the owner, 4 Nov 2026). What is settled is below: the rules
any layout keeps, the modules and their counts, and the IMUs. Distances are estimates unless a
source is named. What the electrodes and the strips are made of is under
[Rubaška](../rubaska/CONSTRUCTION.md#electrodes).

## The electrodes' rules

- **Every channel differential,** P against N, on every unit; no reference electrode (the owner,
  3 Nov 2026). Every chip an ADS1298: a module of the body or the head two, 16 channels on 32
  electrodes and a bias electrode, 33; the neck's one, 8 channels on 16 electrodes and a bias, 17;
  512 on the modules, and the glove's and the sock's sixteen with a bias each, 580 in all.
- **What a pair sees.** Along the fibres a pair catches the potential running down them at two
  points, a large difference from one muscle: SENIAM's pair, 20 mm apart along the fibres (its
  sensor pages, seniam.org). Each electrode sees most the muscle under it, so a chord from one
  muscle to its neighbour gives their difference; of the muscles between its ends it sees mostly the
  fibres running along it, while a muscle crossing it square at its middle nearly cancels (a lead's
  reciprocity, from general physics; Malmivuo & Plonsey, *Bioelectromagnetism*, 1995, to be read for
  it). **A pair across a narrow muscle sees little,** both its ends over the same fibres' potential,
  and it sees a difference only when its ends lie over different muscles, or far apart on a broad
  one (an inference). A little lean adds some of the running potential (an inference). Mixed along
  and across pairs held up best when the electrodes shifted (Young et al., IEEE TBME 58, 2011; 59,
  2012, the forearm only). Crosstalk grows with the distance, ~36 % at 2 cm and ~49 % at 4 cm in one
  case (De Luca et al., J Biomech 45, 2012): for a learned model the mix is the signal (an
  inference).
- **On small muscles and near the heart 2–3 cm:** the hand, the foot, the head, the
  sternocleidomastoid, the left chest; SENIAM's own distance is 20 mm on most muscles' pages and
  5–7.5 mm on the abductor pollicis brevis' (seniam.org).
- **No two electrodes closer than 1.5 cm,** 1 cm on the hand and the foot, where the discs are
  small, and an IMU 1 cm from anything.
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
- **The bias over bone,** as SENIAM puts its reference electrode over bone (C7, the wrist, the
  ankle). Where an IMU needs the same bone, both stay on it a few centimetres apart (see [the
  IMUs](#the-imus)). One bias electrode drives the body and the others wait as spares (see
  [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)).
- **A strip does not stretch:** an elastic gap in the band's fabric takes the swell, and two or
  three short strips a module, ~20 cm at most, meet at it (see
  [Rubaška](../rubaska/CONSTRUCTION.md#electrodes)).
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
- **Nothing in the hair:** the head's electrodes lie on the forehead below its hairline, on the
  temples, and on a strip above the ears no higher than an edge that can be shaved, as under a
  bowl cut, ~4 cm above the ear; the crown and the back of the head carry no electrodes, only the
  IMUs and Nataša. Where the hair begins differs from head to head: the places here are an average
  forehead's, an estimate.
- **Nothing where the body is pressed:** the palm, which a grip presses, the sole, stood on, and
  the seat, sat on, stay bare, the electrodes there wandering in the signal; and the backpack's
  straps, its belt and its back panel press too, so neither an electrode nor an IMU sits under
  their path, the straps padded past the shoulders' units (see
  [Rubaška](../rubaska/CONSTRUCTION.md#open-questions)). What else was left
  out, and why, is under [WHY](WHY.md).

## The modules

Sixteen modules on the body, one a piece of the suit: the head (the headband's front half, Nataša
on its back half), the neck with the upper back, the two shoulders, the chest with the abdomen,
the lower back, the two hips, the two upper arms, the two forearms, the two thighs and the two
calves; the hand's and the foot's eight channels on the glove's and the sock's own ADS1298. A
module of the body and the head's have 32 electrodes and a bias each, the neck's 16 and a bias,
the hand's and the foot's 16 and a bias. **Where they sit on each module is not laid out:** it
waits for the professionals' advice; what was tried is under
[WHY](WHY.md#the-layouts-tried).

## What it comes to

| part | modules | P + N | bias | IMUs |
|---|---|---|---|---|
| head | 1 | 32 | 1 | 4 |
| neck and upper back | 1 | 16 | 1 | 4 |
| shoulders | 2 | 64 | 2 | 6 |
| chest and abdomen | 1 | 32 | 1 | 1 |
| lower back | 1 | 32 | 1 | 3 |
| hips | 2 | 64 | 2 | 2 |
| upper arms | 2 | 64 | 2 | 8 |
| forearms | 2 | 64 | 2 | 4 |
| hands, the gloves | 2 | 32 | 2 | 48 |
| thighs | 2 | 64 | 2 | 8 |
| calves | 2 | 64 | 2 | 4 |
| feet, the socks | 2 | 32 | 2 | 16 |
| **the suit** | **16 modules, 2 gloves, 2 socks** | **560** | **20, 580 electrodes in all** | **108** |

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

- **Four IMUs a module at most:** two I3C buses of two, since the LSM6DSV16X has one address pin,
  SDO/SA0, for 0x6A or 0x6B, and its I3C identity differs only by it (DS13510 Rev 4, 5.1.2 and
  table 17); 64 places on 16 modules, 44 fitted. The gloves come on top, 24 each, and the
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
  with one ADS1298 and the IMUs, the glove's 24, a sock's eight to start (see
  [Rubaška](../rubaska/HARDWARE.md#the-glove)); the forearm's and the calf's modules keep their
  two.

| module | IMUs | places |
|---|---|---|
| head (headband) | 4 | a square on the skull, one rigid bone: the forehead's two over the frontal bone, left and right of Míša's housing above the frontalis' pairs, the middle being his, with his own IMU; the back half's two above the ears' level beside Nataša's board, left and right. Four on one bone are redundancy: their mean halves the noise, and a band that slips shows as the four disagreeing |
| neck and upper back | 4 | C2's spinous process, the first felt below the skull; C5; T2, between the shoulder blades' tops; T6, between their lower halves (the blade's lower angle lies at T7, Gray 1918); the neck and the upper back bend at every level (an estimate). C5, T2 and T6 lie under the backpack's back panel, so the panel is suspended off the spine or carries a channel there (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)) |
| shoulder, each | 3 | the acromion's flat top, 2–3 cm off the backpack strap's path, which runs over the acromion and the clavicle: the scapula followed from it, with an error under 10°, between 30° and 120° of the arm's elevation (Karduna et al., J Biomech Eng 2001; the figures from a later review, PMC4019455); the scapula's spine, its outer part; the clavicle's middle, near the skin |
| chest and abdomen | 1 | the sternum's body, its middle |
| lower back | 3 | the thoracolumbar junction, T12–L1; L3's spinous process, for the lumbar curve; the sacrum's top, S1, the pelvis' sensor |
| hip, each | 1 | the iliac crest's tubercle, in front on its outer lip, a second look at the pelvis' tilt; the backpack's hip belt, if one is worn, runs over the crest, so the belt is padded clear of it or the IMU sits a finger's breadth below the crest |
| upper arm, each | 4 | the outer side at the deltoid's insertion; the lowest on the lateral supracondylar ridge, just above the lateral epicondyle; above the medial epicondyle, in front of the ulnar nerve's groove; the back above the olecranon |
| forearm, each | 2 | the ulna's border 3–4 cm below the olecranon; the radius' back ~2 cm above the wrist, on the radius alone, which turns with the hand while the ulna does not; the hand's are the glove's (below) |
| thigh, each | 4 | 5 cm below the greater trochanter's tip on the outer side; 4–5 cm above the lateral and the medial epicondyle; the front above the patella (estimate) |
| calf, each | 2 | the tibia's inner surface 3–4 cm below the knee and 6–8 cm above the ankle; the foot's are the sock's (below) |

| | IMUs |
|---|---|
| the body's modules | 44 of 64 places |
| the gloves | 2 × 24 |
| the socks | 2 × 8 |
| all, with two gloves and two socks | 108 |

### The glove's

The glove's board on the back of the hand carries the hand's ADS1298 and 24 IMU places in six zones
of four, two to a branch on Staršaja's two switched I3Cs (see
[Rubaška](../rubaska/HARDWARE.md#the-glove)). **The electrodes,** eight channels, wait with the rest
(above). **The IMUs,** 24, a zone a finger and the sixth over the carpal bones: on each finger its
three phalanges, the proximal and the middle on its branch A, the distal on its branch B with a
place to spare; the thumb's metacarpal and proximal phalanx on its A, its distal and the board's
own, on the back of the hand over the carpus, on its B; the four spares: the third, fourth and fifth
metacarpals' heads, where the palm's arch bends, on the middle, ring and little fingers' B, and a
second on the thumb's metacarpal, because its skin slides, on the index finger's B, whose strip runs
beside the thumb's base. Over bone, not between the bones, where the interosseous muscles bulge
under the skin; the strips along the sides of the fingers. Which are fitted the recordings decide:
all 24; 12, the thumb's three, the board's own and two a finger, the proximal and the distal; or 8,
the thumb's three, the board's own and one a finger, the proximal, a mitt open at the fingers for a
hand without a glove. The palm's arch bending only past the middle finger is anatomy, not measured
here. Where on the carpus the four sit, and whether IMUs on its skin follow its bones or the skin
sliding over them, the first glove shows.

### The socks

Nosok's board sits on the calf above the ankle (see [Rubaška](../rubaska/HARDWARE.md#the-sock)); on
the foot its ADS1298's sixteen electrodes, eight channels waiting with the rest, and eight IMUs to
start, of the board's 24 places, the segments of a multi-segment foot model, the Oxford Foot Model's
hindfoot, forefoot and hallux (Stebbins et al., Gait & Posture 23, 2006): the heel over the
calcaneus, the midfoot's inner side, the fourth metatarsal and the hallux's proximal phalanx, four
laid out, the other four for trials, the forefoot's outer side and the lesser toes among them, all
in Staršaja's zones as the glove's; over bone, not on the sole, which is stood on, and clear of the
foot's electrodes; the first places a proposal.

## Open questions

- **the electrodes' places on every module,** asked of professionals (4 Nov 2026); then checked on
  a body by the first recordings, the first arm first, before a strip is drawn in a series, each
  layout ranked by what its EMG gives alone and adds to the IMUs, tested on a new putting-on of
  the sleeve (see [Baťa](../bata/SIGNALS.md#the-model));
- **the sock's IMU places on the foot** beyond the first four, the heel, the midfoot, the forefoot
  and the hallux being Staršaja's own, with the hand's layout;
- how far apart a pair may sit: no source found gives a limit;
- the hand, asked before any glove is made, since each version of it is a flexible circuit made
  and thrown away: its electrodes' strip under the board and the finger strips on one inner
  layer; and how many of the glove's eight channels the thumb wants: the opponens lies beneath the
  abductor pollicis brevis along the first metacarpal, the short flexor and the adductor in the
  palm, and the long flexor in the forearm (Gray 1918, pp. 461–462);
- 20 IMU places left free on the modules, for trials; the heel is the sock's;
- the bands' sizes, S, M and L, and how much of a body the elastic gaps take up; how much the
  model loses after the suit comes off and goes on again.

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
hypersensitivity; TI's ADS1298 datasheet, SBAS459K. For the IMUs: Xsens MVN's 17 segments in
PMC3651313; Peters et al., *Quantification of soft tissue artifact in lower limb human motion
analysis: a systematic review*, Gait & Posture 2010; Stagni et al., Clin Biomech 2005 (thigh up to
31 mm, shank up to 21 mm); Cutti et al., *Soft tissue artefact assessment in humeral axial
rotation*, Gait & Posture 21, 2005; Warner & Heller, J Biomech 2025; Karduna et al., *Dynamic
measurements of three-dimensional scapular kinematics: a validation study*, J Biomech Eng 2001,
with the review PMC4019455; Stebbins et al., *Repeatability of a model for measuring multi-segment
foot kinematics in children*, Gait & Posture 23, 2006, the Oxford Foot Model; ST's LSM6DSV16X
datasheet, DS13510 Rev 4.
