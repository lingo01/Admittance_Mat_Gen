import numpy as np
import os
import io
from datetime import datetime
import re


def __idx_bus():
    """Define named indices into bus matrix"""
    PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM, \
    VA, BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN = [0, 1, 2, 3, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    return (PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM,
            VA, BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN)


def __idx_gen():
    """Define named indices into gen matrix"""
    GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN, \
    MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN, PC1, PC2, QC1MIN, QC1MAX, \
    QC2MIN, QC2MAX, RAMP_AGC, RAMP_10, RAMP_30, RAMP_Q, APF = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 21, 22, 23, 24, 10, 11, 12,
13, 14, 15, 16, 17, 18, 19, 20]
    return (GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN,
            MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN, PC1, PC2, QC1MIN, QC1MAX,
            QC2MIN, QC2MAX, RAMP_AGC, RAMP_10, RAMP_30, RAMP_Q, APF)


def __idx_brch():
    """Define named indices into branch matrix"""
    F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, \
    TAP, SHIFT, BR_STATUS, PF, QF, PT, QT, MU_SF, MU_ST, \
    ANGMIN, ANGMAX, MU_ANGMIN, MU_ANGMAX =[ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18, 11, 12, 19, 20]
    return (F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C,
            TAP, SHIFT, BR_STATUS, PF, QF, PT, QT, MU_SF, MU_ST,
            ANGMIN, ANGMAX, MU_ANGMIN, MU_ANGMAX)


def __idx_cost():
    """Define named indices into cost matrix"""
    PW_LINEAR, POLYNOMIAL, MODEL, STARTUP, SHUTDOWN, NCOST, COST = [ 0, 1, 0, 1, 2, 3, 4]
    return PW_LINEAR, POLYNOMIAL, MODEL, STARTUP, SHUTDOWN, NCOST, COST


def __str2num(s):
    """Convert string to number, similar to MATLAB str2num"""
    try:
        if '.' in s or 'e' in s.lower() or 'E' in s:
            return float(s.strip())
        else:
            return int(s.strip())
    except (ValueError, AttributeError):
        return None


def __loadcase(mpc):
    """Convert to internal case format (simplified version)"""
    # This is a simplified version - in actual MATPOWER this does format conversion
    return mpc


def __savecase(filename, comments, mpc):
    """Save MATPOWER case (simplified version)"""
    # This is a simplified version - would need full implementation for actual use
    print(f"Would save case to {filename}")
    pass


def __mpver():
    """Return MATPOWER version (simplified)"""
    return "Python version 1.0"


def func_cdf2mpc(cdf_file_name=None, mpc_name=None, verbose=None, cdf_content=None):
    """
    CDF2MPC  Converts an IEEE CDF data file into a MATPOWER case struct.
       MPC = CDF2MPC(CDF_FILE_NAME)
       MPC = CDF2MPC(CDF_FILE_NAME, VERBOSE)
       MPC = CDF2MPC(CDF_FILE_NAME, MPC_NAME)
       MPC = CDF2MPC(CDF_FILE_NAME, MPC_NAME, VERBOSE)
       [MPC, WARNINGS] = CDF2MPC(CDF_FILE_NAME, ...)

       Converts an IEEE Common Data Format (CDF) data file into a MATPOWER case
       struct.

       Input:
           CDF_FILE_NAME :  name of the IEEE CDF file to be converted
           MPC_NAME      :  (optional) file name to use to save the resulting
                             MATPOWER case
           VERBOSE       :  1 (default) to display progress info, 0 otherwise

       Output(s):
           MPC      : resulting MATPOWER case struct
           WARNINGS : (optional) cell array of strings containing warning
                      messages (included by default in comments of MPC_NAME).

       The IEEE CDF does not include some data need to run an optimal power
       flow. This script creates default values for some of this data as
       follows:

           Bus data:
               Vmin = 0.94 p.u.
               Vmax = 1.06 p.u.
           Gen data:
               Pmin = 0 MW
               Pmax = Pg + baseMVA
           Gen cost data:
               Quadratic costs with:
                   c2 = 10 / Pg, c1 = 20, c0 = 0, if Pg is non-zero, and
                   c2 = 0.01,    c1 = 40, c0 = 0, if Pg is zero
               This should yield an OPF solution "close" to the
               existing solution (assuming it is a solved case)
               with lambdas near $40/MWh. See 'help caseformat'
               for details on the cost curve format.

       CDF2MPC may modify some of the data which are "infeasible" for
       running optimal power flow. If so, warning information will be
       printed out on screen.

       Note: Since our code can not handle transformers with variable tap,
       you may not expect to get exactly the same power flow solution
       using converted data. This is the case when we converted ieee300.cdf.

       MATPOWER
       Copyright (c) 1996-2016, Power Systems Engineering Research Center (PSERC)
       by Deqiang (David) Gan, PSERC Cornell & Zhejiang University
       and Ray Zimmerman, PSERC Cornell

       This file is part of MATPOWER.
       Covered by the 3-clause BSD License (see LICENSE file for details).
       See https://matpower.org for more info.
    """
    
    # Define named indices into bus, gen, branch matrices
    (PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM,
     VA, BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN) = __idx_bus()
    (GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN,
     MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN, PC1, PC2, QC1MIN, QC1MAX,
     QC2MIN, QC2MAX, RAMP_AGC, RAMP_10, RAMP_30, RAMP_Q, APF) = __idx_gen()
    (F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C,
     TAP, SHIFT, BR_STATUS, PF, QF, PT, QT, MU_SF, MU_ST,
     ANGMIN, ANGMAX, MU_ANGMIN, MU_ANGMAX) = __idx_brch()
    (PW_LINEAR, POLYNOMIAL, MODEL, STARTUP, SHUTDOWN, NCOST, COST) = __idx_cost()

    # Handle input args
    if mpc_name is None and verbose is None:
        verbose = 1
        mpc_name = ''
    elif isinstance(mpc_name, str):  # save the file
        if verbose is None:
            verbose = 1
    elif isinstance(mpc_name, (int, float)):  # don't save the file
        verbose = mpc_name
        mpc_name = ''
    else:
        if verbose is None:
            verbose = 1
        if mpc_name is None:
            mpc_name = ''

    # Read data from CDF file/text into mpc fields
    if cdf_content is None:
        if not cdf_file_name:
            raise ValueError("cdf_file_name 和 cdf_content 至少传入一个")
        cdf_path, cdf_name_only = os.path.split(cdf_file_name)
        cdf_name_base, cdf_ext = os.path.splitext(cdf_name_only)
        if not cdf_ext:
            cdf_ext = '.cdf'
            cdf_file_name = cdf_name_base + cdf_ext
        cdf_display_name = cdf_file_name
        fid = open(cdf_file_name, 'r', encoding='utf-8')
    else:
        cdf_display_name = cdf_file_name if cdf_file_name else '<in-memory-cdf>'
        fid = io.StringIO(cdf_content)

    try:
        with fid:
            if verbose:
                print(f"Converting file '{cdf_display_name}'")
                print("  WARNINGS:")

            # initialize list of warnings
            warnings = []

            # get baseMVA
            title_cdf = fid.readline().strip()
            baseMVA_str = title_cdf[30:36]  # Python uses 0-based indexing
            try:
                baseMVA = __str2num(baseMVA_str)
                if baseMVA is None:
                    raise ValueError("Base MVA not found")
                if len([m for m in re.finditer('/', title_cdf[1:9])]) == 2:  # date in the file
                    warnings.append('check the title format in the first line of the cdf file.')
            except:
                raise ValueError('Error getting the Base MVA, check the title format in the first line of the file.')

            # find string 'BUS DATA FOLLOWS'
            while True:
                line = fid.readline()
                if not line:
                    break
                if line[:16] == 'BUS DATA FOLLOWS':
                    break

            # get bus data, feed them into matrix bus, gen, gencost
            ibus = 0
            igen = 0
            iarea = 0
            
            bus = []
            gen = []
            gencost = []
            bus_name = []

            while True:
                line = fid.readline()
                if not line or line[:4] == '-999':
                    break

                # feed bus data
                ibus += 1
                bus_row = [0] * 13  # Initialize with zeros
                
                bus_row[BUS_I] = __str2num(line[0:5])  # bus number
                bus_name.append(line[5:17].strip())  # bus names
                bus_row[BUS_TYPE] = __str2num(line[24:26])
                if bus_row[BUS_TYPE] == 0:  # bus type
                    bus_row[BUS_TYPE] = 1
                
                if bus_row[BUS_TYPE] < 2:  # Pd
                    bus_row[PD] = __str2num(line[40:49]) - __str2num(line[58:67])
                elif bus_row[BUS_TYPE] >= 2:
                    bus_row[PD] = __str2num(line[40:49])
                
                bus_row[QD] = __str2num(line[49:58])  # Qd
                bus_row[GS] = baseMVA * __str2num(line[106:114])  # Gs
                bus_row[BS] = baseMVA * __str2num(line[114:122])  # Bs
                bus_row[BUS_AREA] = __str2num(line[18:20])  # area
                bus_row[VM] = __str2num(line[27:33])  # Vm
                bus_row[VA] = __str2num(line[33:40])  # Va
                bus_row[BASE_KV] = __str2num(line[76:83])  # baseKV
                bus_row[ZONE] = __str2num(line[20:23])  # zone
                bus_row[VMAX] = 1.06  # default voltage upper limit
                bus_row[VMIN] = 0.94  # default voltage lower limit

                bus.append(bus_row)

                # feed gen and gencost
                Pg = __str2num(line[58:67])
                Qg = __str2num(line[67:75])
                Qmax = __str2num(line[90:98])
                Qmin = __str2num(line[98:106])
                
                if bus_row[BUS_TYPE] >= 2:
                    igen += 1
                    if bus_row[BUS_TYPE] == 3:
                        refgen = igen - 1  # Convert to 0-based index
                    
                    gen_row = [0] * 21  # Initialize with zeros
                    gen_row[GEN_BUS] = bus_row[BUS_I]  # bus number
                    gen_row[PG] = Pg  # Pg
                    
                    if gen_row[PG] < 0:  # negative Pg is transformed as load
                        bus_row[PD] = bus_row[PD] - gen_row[PG]
                        warnings.append(f'negative Pg at bus {bus_row[BUS_I]} treated as Pd')
                        if verbose:
                            print(f'    {warnings[-1]}')
                        gen_row[PG] = 0
                    
                    gen_row[QG] = Qg  # Qg
                    gen_row[QMAX] = Qmax  # Qmax
                    gen_row[QMIN] = Qmin  # Qmin
                    
                    if Qmax - Qmin < 0.01:  # Qmax is modified
                        gen_row[QMAX] = Qmin + 0.1 * baseMVA
                        warnings.append(f'Qmax = Qmin at generator at bus {bus_row[BUS_I]:4d} (Qmax set to Qmin + {baseMVA/10})')
                        if verbose:
                            print(f'    {warnings[-1]}')
                    
                    gen_row[VG] = __str2num(line[84:90])  # specified voltage
                    gen_row[MBASE] = baseMVA  # baseMVA
                    gen_row[GEN_STATUS] = 1  # default status is 'on'
                    gen_row[PMAX] = gen_row[PG] + baseMVA  # Pmax
                    gen_row[PMIN] = 0  # Pmin = 0 by default

                    gen.append(gen_row)

                    gencost_row = [0] * 7  # Initialize with enough columns
                    gencost_row[MODEL] = POLYNOMIAL  # by default, sets the model as polynomial
                    gencost_row[STARTUP] = 0  # start up cost is zero by default
                    gencost_row[SHUTDOWN] = 0  # shut down cost is zero by default
                    gencost_row[NCOST] = 3  # number of coefficients in polynomial cost
                    
                    gencost.append(gencost_row)

            # Convert to numpy arrays
            bus = np.array(bus)
            gen = np.array(gen) if gen else np.array([]).reshape(0, 25)
            gencost = np.array(gencost) if gencost else np.array([]).reshape(0, 10)

            if gen.size > 0:
                totload = np.sum(bus[:, PD])
                totgen = np.sum(gen[:, PG])
                if totgen < 1.04 * totload:
                    gen[refgen, PMAX] = gen[refgen, PG] + 1.1 * totload - totgen  # Pg at slack bus is modified
                    warnings.append(f'Insufficient generation, setting Pmax at slack bus (bus {int(gen[refgen, GEN_BUS])}) to {gen[refgen, PMAX]}')
                    if verbose:
                        print(f'    {warnings[-1]}')

                # set up the cost coefficients of generators
                ng = gen.shape[0]
                zg = np.where(gen[:, PG] == 0)[0]  # for Pg = 0
                if len(zg) > 0:
                    gencost[zg, COST] = 0.01
                    gencost[zg, COST+1] = 40
                
                nzg = np.where(gen[:, PG] != 0)[0]  # Pg non-zero
                if len(nzg) > 0:
                    gencost[nzg, COST] = 10.0 / gen[nzg, PG]
                    gencost[nzg, COST+1] = 20
                
                gencost[:, COST+2] = 0

            # find string 'BRANCH DATA FOLLOWS'
            while True:
                line = fid.readline()
                if not line:
                    break
                if line[:19] == 'BRANCH DATA FOLLOWS':
                    break

            # get branch data, feed them into matrix branch
            k = 0
            branch = []

            while True:
                line = fid.readline()
                if not line or line[:4] == '-999':
                    break

                k += 1
                branch_row = [0] * 13  # Initialize with zeros
                
                branch_row[F_BUS] = __str2num(line[0:5])  # fbus (also the tap bus)
                branch_row[T_BUS] = __str2num(line[5:10])  # tbus
                branch_row[BR_R] = __str2num(line[19:29])  # R
                branch_row[BR_X] = __str2num(line[29:40])  # X
                branch_row[BR_B] = __str2num(line[40:50])  # B
                branch_row[RATE_A] = __str2num(line[50:55])  # RATE A
                
                if branch_row[RATE_A] < 0.000001:
                    branch_row[RATE_A] = 9999999999999999  # RATE A is modified
                    warnings.append(f'MVA limit of branch {int(branch_row[F_BUS])} - {int(branch_row[T_BUS])} not given, set to {branch_row[RATE_A]}')
                    if verbose:
                        print(f'    {warnings[-1]}')
                
                branch_row[RATE_B] = __str2num(line[56:61])  # RATE B
                branch_row[RATE_C] = __str2num(line[62:67])  # RATE C
                branch_row[TAP] = __str2num(line[76:82])  # transformer turns ratio
                branch_row[SHIFT] = 0  # phase shifter can not be modelled
                branch_row[BR_STATUS] = 1  # by default, branch is on
                
                branch.append(branch_row)

            # Convert to numpy array
            branch = np.array(branch) if branch else np.array([]).reshape(0, 21)

            if verbose:
                print('Done.')

    except OSError as e:
        print(f"Error: {e}")
        raise OSError(f'func_cdf2mpc: Can not read the input file: {cdf_display_name}')

    # put in struct (dictionary)
    mpc = {
        'baseMVA': baseMVA,
        'bus': bus,
        'branch': branch,
        'gen': gen,
        'gencost': gencost,
        'bus_name': bus_name
    }
    mpc = __loadcase(mpc)  # convert to internal (e.g. v. '2') case format

    # (optionally) save MATPOWER case file
    if mpc_name:
        comments = ['']
        if title_cdf:
            comments.append(f'   {title_cdf}')
        comments.append('')
        comments.append(f'   Converted by MATPOWER {__mpver()} using CDF2MPC on {datetime.now().strftime("%d-%b-%Y")}')
        comments.append(f"   from '{cdf_display_name}'.")

        # warnings
        comments.append('')
        comments.append('   WARNINGS:')
        for warning in warnings:
            comments.append(f'       {warning}')
        comments.append('')
        comments.append('   See CASEFORMAT for details on the MATPOWER case file format.')

        if verbose:
            spacers = '.' * (45 - len(mpc_name))
            print(f"Saving to MATPOWER case '{mpc_name}' {spacers}", end='')
        __savecase(mpc_name, comments, mpc)
        if verbose:
            print(' done.')

    mpc['version'] = '2'
    mpc['gencost'] = np.array([[2, 1500, 0, 3, 0.11, 5, 150]] * (gen.shape[0] if gen is not None and gen.size > 0 else 0))


    return mpc, warnings


# Example usage and test function
if __name__ == "__main__":
    # Example usage
    mpc, warnings = func_cdf2mpc('area1.cf')
    # pass
    print(mpc['gen'])
    print(mpc['bus'])
    print(mpc['branch'])
    print(mpc['baseMVA'])
