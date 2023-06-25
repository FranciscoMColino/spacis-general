#include <ArduinoJson.h>

int seq_sz = pow(2, 12) - 1;
long unsigned *transmission_sequence = (long unsigned*)malloc(sizeof(long unsigned) * (long unsigned)ceil((float)seq_sz/32)); //{0xf807fe00,0x7f81ff03,0x1fc0fe0,0x1fe01fc,0x80fe01fc,0x807f80ff,0x1fe01ff,0x7f803fe,0x7f00f80,0x803f81fc,0x1fc1ff,0x7f007f8,0x3e01fe0,0x80ff81fe,0xe007f81f,0xf03fe07f,0xe01fc01f,0x7f001f,0x7e01f8,0xff801fc,0x3fe03fe0,0xe001ff00,0xf803f81f,0x3ff807,0xf80fe07e,0xe03ff01f,0x803fc01f,0xe01f807f,0xc03fe01f,0xe01f801f,0xe01f801f,0xc07f801f,0x1ff807f,0x7fe00ff8,0x1fc0ff80,0x1fe007e0,0x7fe007f8,0x1fc07f80,0x3fc07e00,0xfe007f80,0xf807ff81,0xff81ff01,0xfe01ff01,0x1f81f80,0x7f801fe,0x7f807f8,0x7f01ff0,0x7e01fc,0x7f8007fc,0xfe007e00,0x1f81fe01,0x7f801f80,0x1fe07ff0,0x7fc07ff0,0x1fe01fc0,0x1ff00fe0,0x81fe01f8,0xe00fe07f,0xe03fc00f,0xfe00f81f,0xfe07f807,0x1fe07f01,0x1f803f8,0x3f803fe,0x1ff81fe,0x1ff80ff,0x7fc03fe,0x1f8007f0,0x3f807e0,0x81ff807f,0x7f8003f,0x1fe007e0,0x1fc07e0,0xf03f81ff,0xe07fe007,0x801fe07f,0x1fe01f,0x3f800fe,0x1f800fc,0x7fc01ff8,0xfe007fc0,0xf01fe001,0xf007f807,0xc0fe007f,0xe01ff81f,0x803fe07f,0x807f807f,0xc03fe03f,0x801f807f,0x801fe03f,0x803fe01f,0x807f80ff,0x1ff803ff,0xff807fe0,0x7e01f81,0xff01fc0,0x7f807fe0,0xfe003f80,0x7f807f80,0xff01fe00,0xfe01f807,0xfe01ff01,0x3f81fe01,0x3fe03f0,0xff807f8,0x3fe007f0,0x1f807e0,0xff800fe,0x7e007f80,0xfe03fe00,0x1f803f03,0x7fe07f80,0x7fe03fc0,0x3f807f80,0x1fc01fe0,0x3f81fe0,0xe07f81fc,0x801fe01f,0xf83fe07f,0xf007fe01,0x7e03fe07,0x7f81fc0,0x7fe01f8,0x1fe07f8,0x1fe01ff,0x7fe01ff,0x7e007f8,0xfe01f80};

unsigned no_polynomial = 4;
int polynoms_sizes[4] = {4, 6, 6, 4};
int polynomial_array[4][6] = {
  {12,  8, 5, 1, 0, 0},
  {12, 10, 8, 7, 4, 1},
  {12, 11, 8, 5, 4, 2},
  {12, 10, 9, 3, 0, 0}
};
unsigned current_polynom = 0;

// delays for pin 8->13
unsigned delay_offsets[] = {0, 3, 0, 0, 0, 0};

const uint16_t t1_load = 0;
const uint16_t t1_comp = 1250; //1250
//const uint16_t t1_comp = 1250;

volatile int acc = 1;
unsigned tx_bits = 0;

unsigned long setup_timer1_start = 0;

unsigned int time_between_tx = 20; //seconds between each transmission start
unsigned int time_safe = 5; //time before next transmission where no action is taken
unsigned int acc_jitter = 0;
long unsigned elapsed = 0;

// PROGRAM STATES
unsigned const START_S = 0;
unsigned const TIMER1_WORKING = 1;
unsigned const TIMER1_FINISHED = 2;
unsigned const SEQUENCE_CYCLE = 3;
unsigned const DATA_TRANSFER = 4;
unsigned const WAITING_PHASE = 5;
unsigned int current_state = START_S;

void reset_timer1(){ 
  //Reset Timer1 Control Reg A
  TCCR1A = 0;
  TCCR1B = 0;
}

void setup_timer1(){
 
  // Set CTC mode (resets load after reaching comp goal)
  TCCR1B &= ~(1 << WGM13);
  TCCR1B |= (1 << WGM12);

  // Set to prescaler of 8
  TCCR1B &= ~(1 << CS12);
  TCCR1B |= (1 << CS11);
  TCCR1B &= ~(1 << CS10);

  // Reset Timer1 and set compare value
  TCNT1 = t1_load;
  OCR1A = t1_comp;

  // Enable Timer1 compare interrupt
  TIMSK1 = (1 << OCIE1A);
}

void preliminary_pseudorandom_binary_sequence(int* polynomial_array, int size_pa, int generator_resolution, long unsigned* result){
  
    long unsigned cur = pow(2, generator_resolution) - 1;
    int sequence_size = pow(2, generator_resolution) - 1;
    for (int i = 0; i < sequence_size; i++){
        long unsigned prbs_res = 0;
        prbs_res = (cur >> polynomial_array[0]);
        for (int j = 1; j < size_pa; j++){
            prbs_res = prbs_res ^ (cur >> polynomial_array[j]);
        }
        prbs_res = prbs_res & 1;
        cur = (cur << 1) | prbs_res;
        unsigned array_place = i/32;
        unsigned element_place = i%32;
        result[array_place] = result[array_place] | (prbs_res << element_place);
    }
}

void transform_sequence(long unsigned* preliminary_sequence, unsigned sequence_res, long unsigned* transformed_sequence){
    int sequence_size = pow(2, sequence_res) - 1;
    int ps_size = (long unsigned)ceil((float)sequence_size/32);
    unsigned acc = 0;
    unsigned array_place = 0;
    unsigned element_place = 0;
    long unsigned bit = 0;
    long unsigned new_bit = 0;
    memcpy(transformed_sequence, preliminary_sequence, sizeof(long unsigned) * (long unsigned)ceil((float)sequence_size/32));
    for (int i = 0; i < sequence_size; i++){
        array_place = i/32;
        element_place = i%32;
        bit = ((preliminary_sequence[array_place] >> element_place) & 1) << element_place;
        acc += bit ? 3 : 1;
        new_bit = (acc/16)%2;
        transformed_sequence[array_place] = transformed_sequence[array_place] & ~(1 << element_place);
        transformed_sequence[array_place] = transformed_sequence[array_place] | (new_bit << element_place);
    }
}

void gen_next_seq(){
    current_polynom++;
    current_polynom= current_polynom % 4;
    int sequence_res = 12;
    int sequence_size = pow(2, sequence_res) - 1;
    
    long unsigned* preliminary_sequence = (long unsigned*)malloc(sizeof(long unsigned) * (long unsigned)ceil((float)sequence_size/32));
    free(transmission_sequence);
    transmission_sequence = (long unsigned*)malloc(sizeof(long unsigned) * (long unsigned)ceil((float)sequence_size/32));
    
    memset(transmission_sequence, 0, sizeof(long unsigned) * (long unsigned)ceil((float)sequence_size/32));
    memset( preliminary_sequence, 0, sizeof(long unsigned) * (long unsigned)ceil((float)sequence_size/32));

    preliminary_pseudorandom_binary_sequence(polynomial_array[current_polynom], polynoms_sizes[current_polynom], 12, preliminary_sequence);
    transform_sequence(preliminary_sequence, sequence_res, transmission_sequence);
    
    free(preliminary_sequence);
}

void setup() {
  Serial.begin(115200);
  DDRB = B00111111;

  gen_next_seq();
  
  // Enable global interrupts
  sei();

  // Timer1 controls the 625us delay between impulse update
  // reset_timer1();
  // setup_timer1();
}

void loop() {
  elapsed = micros() - setup_timer1_start;
  switch (current_state) {
    case START_S:
      Serial.println("----- START -----");
      Serial.println(micros());
      acc_jitter = micros() % (time_between_tx * 1000000);
      Serial.println(acc_jitter);
      Serial.println(transmission_sequence[0], HEX);
      current_state = TIMER1_WORKING;
      reset_timer1();
      setup_timer1_start = micros();
      setup_timer1();
      break;
    case TIMER1_WORKING:
      break;
    case TIMER1_FINISHED:
      Serial.print("Elapsed time on TIMER1_FINISHED: ");
      Serial.println(elapsed);
      free(transmission_sequence);
      current_state = DATA_TRANSFER;
      break;
    case DATA_TRANSFER:
      if (elapsed >= (time_between_tx - time_safe) * (1000000)){
        current_state = SEQUENCE_CYCLE;
        Serial.print("Elapsed time on DATA TRANSFER: ");
        Serial.println(elapsed);
      } else {
        if (Serial.available()) {
          String json_message = Serial.readStringUntil('\n');
          // Parse the JSON message
          StaticJsonDocument<96> doc;
          DeserializationError error = deserializeJson(doc, json_message);
          if (error) {
            Serial.print("Parsing failed: ");
            Serial.println(error.c_str());
          }
          else {
            // Extract the command and value from the JSON
            /*
            if (doc.containsKey("command")) {
              String command = doc["command"].as<String>();
            }*/
            String command = "DELAYS";
            if (command=="DELAYS") {
              JsonArray values = doc["values"];
              int i = 0;
              for (JsonVariant value : values) {
                if (i >= 6 ) {
                  break;
                }
                delay_offsets[i++] = value.as<int>();
              }
              Serial.println("Received delay update message");
            }
            
            else {
              Serial.println("Received unknown");
            }
          }
        }
      }
      break;
    case SEQUENCE_CYCLE:
      Serial.println("Starting sequence cycle");
      gen_next_seq();
      Serial.print("Elapsed time on SEQUENCE_CYCLE: ");
      Serial.println(elapsed);
      current_state = WAITING_PHASE;
      break;
    case WAITING_PHASE:
      if (micros() - setup_timer1_start >= time_between_tx * 1000000 - acc_jitter){
        Serial.print("Elapsed time on WAITING PHASE: ");
        Serial.println(elapsed);
        current_state = START_S; 
      }
      break;
    default:
      break;
  }
} 

ISR(TIMER1_COMPA_vect) {
  PORTB = tx_bits;

  // takes a max of 128us out of 625us (theoretically) available
  tx_bits = 0;
  for (int i = 0; i < 6; i++) {
    int n_acc = acc - delay_offsets[i];
    if (n_acc < 0){
      continue;
    }
    tx_bits = tx_bits | (((transmission_sequence[n_acc/128] >> (n_acc/4%32)) & 1) << i);
  }
  acc++;

  if (acc >= 16380){
    // 4095 * 4 = 16380 
    acc = acc % 16380;
    reset_timer1();
    PORTB = 0;
    current_state = TIMER1_FINISHED;
  } 
}
