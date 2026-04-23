def decision_agent(tech, ml, risk):
    """Make final trading decision based on all agent outputs."""
    # Basic logic
    if (
        tech["Trend"] == "Bullish" and
        ml["Prediction"] == 1 and
        ml["Confidence"] > 0.55 and
        risk["Risk_Level"] != "High Risk"
    ):
        return "BUY"

    elif (
        tech["Trend"] == "Bearish" and
        ml["Prediction"] == 0
    ):
        return "AVOID"

    else:
        return "HOLD"


def make_final_decision(technical_output, ml_output, risk_output):
    """Combine all agent outputs into final decision."""
    final_decision = decision_agent(
        technical_output,
        ml_output,
        risk_output
    )
    
    return {
        "Decision": final_decision,
        "Trend": technical_output["Trend"],
        "ML_Confidence": ml_output["Confidence"],
        "Risk_Level": risk_output["Risk_Level"],
        "Position_Size": risk_output["Position_Size"]
    }


if __name__ == "__main__":
    # Example usage
    technical_output = {
        "Trend": "Bullish",
        "RSI_Signal": "Normal"
    }
    
    ml_output = {
        "Prediction": 1,
        "Confidence": 0.60
    }
    
    risk_output = {
        "Risk_Level": "Medium Risk",
        "Position_Size": 0.5
    }
    
    final_output = make_final_decision(technical_output, ml_output, risk_output)
    print("Final Decision Output:", final_output)