﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using MLAgents;

public class MyRaceAcademy : Academy
{
    public override void AcademyReset()
    {
#if DEVELOPMENT_BUILD
        Debug.unityLogger.logEnabled = true;
#else
        Debug.unityLogger.logEnabled = false;
#endif
        int activeAgents = (int)resetParameters["num_agents"];
        GameObject.Find("AgentManager").GetComponent<AgentManager>().SetAgents(activeAgents);
    }

    public override void AcademyStep()
    {

    }

}
