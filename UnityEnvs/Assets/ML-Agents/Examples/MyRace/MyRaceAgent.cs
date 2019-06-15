﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using MLAgents;

public class MyRaceAgent : Agent
{
    public GameObject ball;
    Vector3 ballStartPos;

    private void Start()
    {
        ballStartPos = ball.transform.position;
    }

    public override void AgentAction(float[] vectorAction, string textAction)
    {
        if(brain.brainParameters.vectorActionSpaceType == SpaceType.continuous)
        {
            gameObject.transform.Rotate(new Vector3(0, 0, 1), vectorAction[0]);
            gameObject.transform.Rotate(new Vector3(1, 0, 0), vectorAction[1]);

            if (IsDone() == false)
            {
                float dist_x = ball.transform.position.x - gameObject.transform.position.x;
                float dist_z = ball.transform.position.z - gameObject.transform.position.z;
                float distFromCenter = dist_x * dist_x + dist_z * dist_z;
                SetReward(1 / (1 + distFromCenter));
            }
        }
        else
        {
            int action = (int)vectorAction[0];
            Debug.Log(action);
            switch (action)
            {
                case 1:
                    gameObject.transform.Rotate(new Vector3(0, 0, -1), 2);
                    break;
                case 2:
                    gameObject.transform.Rotate(new Vector3(0, 0, 1), 2);
                    break;
                case 3:
                    gameObject.transform.Rotate(new Vector3(-1, 0, 0), 2);
                    break;
                case 4:
                    gameObject.transform.Rotate(new Vector3(1, 0, 0), 2);
                    break;
                default:
                    break;
            }
            if (IsDone() == false)
            {
                float dist_x = ball.transform.position.x - gameObject.transform.position.x;
                float dist_z = ball.transform.position.z - gameObject.transform.position.z;
                float distFromCenter = dist_x * dist_x + dist_z * dist_z;
                SetReward( 1 / (1+distFromCenter) );
            }
        }

        if ((ball.transform.position.y - gameObject.transform.position.y) < -2f ||
            Mathf.Abs(ball.transform.position.x - gameObject.transform.position.x ) > 3f ||
            Mathf.Abs(ball.transform.position.z - gameObject.transform.position.z) > 3f )
        {
            Done();
            SetReward(-1f);
        }
    }

    public override void CollectObservations()
    {
        AddVectorObs(gameObject.transform.rotation.z);
        AddVectorObs(gameObject.transform.rotation.x);
        AddVectorObs(ball.transform.GetComponent<Rigidbody>().velocity.x);
        AddVectorObs(ball.transform.GetComponent<Rigidbody>().velocity.y);
        AddVectorObs(ball.transform.GetComponent<Rigidbody>().velocity.z);
        AddVectorObs(ball.transform.position.x - gameObject.transform.position.x);
        AddVectorObs(ball.transform.position.y - gameObject.transform.position.y);
        AddVectorObs(ball.transform.position.z - gameObject.transform.position.z);
    }

    public override void AgentReset()
    {
        gameObject.transform.rotation = new Quaternion(0f, 0f, 0f, 0f);
        ball.GetComponent<Rigidbody>().velocity = new Vector3(0f, 0f, 0f);
        ball.transform.position = ballStartPos;
    }
}
