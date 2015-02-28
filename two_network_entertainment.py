#!/usr/bin/env python

import sys
sys.path.append('/opt/lib/python2.7/site-packages/')

import math
import numpy as np
import pylab
import nest
import nest.raster_plot
import nest.voltage_trace
import nest.topology as tp
import ggplot


nest.ResetKernel()
nest.SetKernelStatus({'local_num_threads': 8})

nr_populations = 2
neuron_model = 'iaf_psc_exp'

model_params = {'tau_m': 10.,        # membrane time constant (ms)
                'tau_syn_ex': 0.5,   # excitatory synaptic time constant (ms)
                'tau_syn_in': 0.5,   # inhibitory synaptic time constant (ms)
                't_ref': 2.,         # absolute refractory period (ms)
                'E_L': -65.,         # resting membrane potential (mV)
                'V_th': -50.,        # spike threshold (mV)
                'C_m': 250.,         # membrane capacitance (pF)
                'V_reset': -65.      # reset potential (mV)
               }

input_rate = 100.
input_degrees = []
input_delays = [1.5, 0.75]
input_weights = 7.
frequencies = [11., 27.]

populations = np.random.normal(100, 10, nr_populations)
# for p in populations:
#   input_degrees.append(np.abs(np.random.normal(p, p/10.)))

input_degrees = [50., 50.]

print input_degrees

populations = np.array(map(int, populations))

neurons = np.zeros_like(populations).tolist()
inputs = np.zeros_like(populations).tolist()
noises = np.zeros_like(populations).tolist()
spikes = np.zeros_like(populations).tolist()
voltmeters = np.zeros_like(populations).tolist()

nest.SetDefaults(neuron_model, model_params)

# create nodes
for ctr in xrange(len(populations)):
  n = nest.Create(neuron_model, populations[ctr])
  neurons[ctr] = n

  i = nest.Create('sinusoidal_poisson_generator')
  nest.SetStatus(i, {
    'dc': input_rate*input_degrees[ctr],
    'ac': input_rate*input_degrees[ctr],
    'freq': frequencies[ctr]
  })
  inputs[ctr] = i

  p = nest.Create('poisson_generator')
  nest.SetStatus(p, {
    'rate': input_rate*input_degrees[ctr]*20.
  })
  noises[ctr] = p

  sp = nest.Create('spike_detector')
  spikes[ctr] = sp

  v = nest.Create('voltmeter')
  voltmeters[ctr] = v


# connect the nodes
prev_pop = None
for ctr in xrange(len(populations)):
  if ctr < (len(populations)-1):
    prev_pop = neurons[ctr+1]
  elif len(populations) == 1:
    prev_pop = neurons[ctr]
  else:
    prev_pop = neurons[ctr-1]

  conn_dict = {
    'rule': 'fixed_total_number',
    'N': populations[ctr]*100
  }

  syn_dict = {
    # 'delay': {
    #   'mu': 1.5,
    #   'distribution': 'normal_clipped',
    #   'sigma': 0.75,
    #   'low': 0.1
    # },
    'delay': 1.5,
    'model': 'stdp_synapse',
    'weight': {
      'distribution': 'normal_clipped',
      'mu': 10.,
      'sigma': 1.,
      'low': 0.0
    }
  }

  nest.Connect(neurons[ctr], prev_pop, conn_dict, syn_dict)

  nest.Connect(inputs[ctr], neurons[ctr], 'all_to_all',
    {'weight': input_weights, 'delay': input_delays[0]})

  nest.Connect(noises[ctr], neurons[ctr], 'all_to_all',
    {'weight': input_weights, 'delay': input_delays[0]})

  nest.Connect(neurons[ctr], spikes[0])
  nest.Connect(inputs[ctr], spikes[0])
  # nest.Connect(voltmeters[0], neurons[ctr])


nest.Simulate(1000)

# for sp in spikes:
nest.raster_plot.from_device(spikes[0], hist=True)

# for v in voltmeters:
  # pylab.figure()
# nest.voltage_trace.from_device(voltmeters[0])

pylab.show()
